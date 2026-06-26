"""Processing job queue and reports."""

from __future__ import annotations

import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Callable

from .ffmpeg_runner import CommandResult, run_command

JOB_FIELDS = [
    "input_path",
    "output_path",
    "preset",
    "start_time",
    "end_time",
    "duration_seconds",
    "status",
    "command",
    "error",
    "log_path",
    "output_size_bytes",
]


@dataclass(slots=True)
class ProcessingJob:
    input_path: Path
    output_path: Path
    preset: str
    command: list[str]
    log_path: Path | None = None
    status: str = "PENDING"
    start_time: str | None = None
    end_time: str | None = None
    duration_seconds: float | None = None
    error: str = ""
    output_size_bytes: int | None = None
    result: CommandResult | None = None
    skip_existing: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "input_path": str(self.input_path),
            "output_path": str(self.output_path),
            "preset": self.preset,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "command": self.command,
            "error": self.error,
            "log_path": str(self.log_path) if self.log_path else None,
            "output_size_bytes": self.output_size_bytes,
        }


def run_job(job: ProcessingJob, dry_run: bool = False) -> ProcessingJob:
    if job.skip_existing and job.output_path.exists():
        job.status = "SKIPPED"
        job.output_size_bytes = job.output_path.stat().st_size
        return job
    job.status = "RUNNING"
    job.start_time = _now()
    started = perf_counter()
    try:
        job.result = run_command(job.command, log_path=job.log_path, dry_run=dry_run)
        if dry_run or job.result.returncode == 0:
            job.status = "SUCCESS"
        else:
            job.status = "FAILED"
            job.error = job.result.stderr.strip() or f"Command failed with exit code {job.result.returncode}."
    except Exception as exc:  # noqa: BLE001 - job failure must not stop the batch.
        job.status = "FAILED"
        job.error = str(exc)
    finally:
        job.end_time = _now()
        job.duration_seconds = round(perf_counter() - started, 3)
        if job.output_path.exists():
            job.output_size_bytes = job.output_path.stat().st_size
    return job


def run_jobs(
    jobs: list[ProcessingJob],
    dry_run: bool = False,
    workers: int = 1,
    on_update: Callable[[ProcessingJob], None] | None = None,
) -> list[ProcessingJob]:
    if workers <= 1:
        results = []
        for job in jobs:
            result = run_job(job, dry_run=dry_run)
            if on_update:
                on_update(result)
            results.append(result)
        return results
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {executor.submit(run_job, job, dry_run): job for job in jobs}
        for future in as_completed(future_map):
            result = future.result()
            if on_update:
                on_update(result)
            results.append(result)
    return results


def write_job_report(jobs: list[ProcessingJob], output_dir: Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "job_report.json"
    csv_path = output / "job_report.csv"
    payload = {
        "generated_at": _now(),
        "total_jobs": len(jobs),
        "success": sum(1 for job in jobs if job.status == "SUCCESS"),
        "failed": sum(1 for job in jobs if job.status == "FAILED"),
        "skipped": sum(1 for job in jobs if job.status == "SKIPPED"),
        "jobs": [job.to_dict() for job in jobs],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=JOB_FIELDS)
        writer.writeheader()
        for job in jobs:
            row = job.to_dict()
            row["command"] = " ".join(job.command)
            writer.writerow({field: row.get(field, "") for field in JOB_FIELDS})
    return json_path, csv_path


def _now() -> str:
    return datetime.now().replace(microsecond=0).isoformat()

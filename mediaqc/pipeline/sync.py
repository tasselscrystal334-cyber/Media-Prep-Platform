"""Media Pipeline sync and transfer reporting."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from mediaqc.hash_check import calculate_sha256
from mediaqc.live_event.manifest import build_manifest, write_manifest
from mediaqc.probe import probe_media
from mediaqc.scanner import scan_media_files

from .mediainfo import probe_mediainfo_optional
from .network import resolve_network_target

TRANSFER_FIELDS = [
    "relative_path",
    "source_path",
    "destination_path",
    "size_bytes",
    "sha256_source",
    "sha256_destination",
    "status",
    "duration_seconds",
    "error",
]


@dataclass(slots=True)
class TransferRecord:
    relative_path: str
    source_path: Path
    destination_path: Path
    size_bytes: int
    sha256_source: str | None = None
    sha256_destination: str | None = None
    status: str = "PENDING"
    duration_seconds: float = 0.0
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "source_path": str(self.source_path),
            "destination_path": str(self.destination_path),
            "size_bytes": self.size_bytes,
            "sha256_source": self.sha256_source,
            "sha256_destination": self.sha256_destination,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
        }


@dataclass(slots=True)
class PipelineSyncResult:
    source: Path
    destination: Path
    profile: str | None
    records: list[TransferRecord] = field(default_factory=list)
    manifest_path: Path | None = None
    manifest_csv_path: Path | None = None
    transfer_json_path: Path | None = None
    transfer_csv_path: Path | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": str(self.source),
            "destination": str(self.destination),
            "profile": self.profile,
            "total_files": len(self.records),
            "success": sum(1 for item in self.records if item.status == "SUCCESS"),
            "failed": sum(1 for item in self.records if item.status == "FAILED"),
            "skipped": sum(1 for item in self.records if item.status == "SKIPPED"),
            "warnings": self.warnings,
            "manifest_path": str(self.manifest_path) if self.manifest_path else None,
            "manifest_csv_path": str(self.manifest_csv_path) if self.manifest_csv_path else None,
            "records": [item.to_dict() for item in self.records],
        }


def run_pipeline_sync(
    source: Path,
    destination: Path,
    output_dir: Path,
    profile: str | None = None,
    skip_existing: bool = False,
    overwrite: bool = False,
    collect_mediainfo: bool = True,
) -> PipelineSyncResult:
    src = Path(source).resolve()
    target = resolve_network_target(destination)
    target.path.mkdir(parents=True, exist_ok=True)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    result = PipelineSyncResult(source=src, destination=target.path.resolve(), profile=profile)
    result.warnings.extend(target.warnings)

    media_files = scan_media_files(src)
    for media in media_files:
        try:
            media.sha256 = calculate_sha256(media.path)
            media.ffprobe = probe_media(media.path)
            if collect_mediainfo:
                mediainfo, warning = probe_mediainfo_optional(media.path)
                if mediainfo is not None:
                    media.ffprobe = {**(media.ffprobe or {}), "mediainfo": mediainfo}
                elif warning:
                    result.warnings.append(f"{media.filename}: {warning}")
        except Exception as exc:  # noqa: BLE001
            media.fail(str(exc))

    manifest = build_manifest(src, project_name=profile or src.name, files=media_files)
    result.manifest_path, result.manifest_csv_path = write_manifest(manifest, output)

    for media in media_files:
        relative = str(Path(media.path).resolve().relative_to(src))
        destination_path = target.path / relative
        record = TransferRecord(
            relative_path=relative,
            source_path=Path(media.path),
            destination_path=destination_path,
            size_bytes=media.size_bytes,
            sha256_source=media.sha256,
        )
        started = perf_counter()
        try:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            if destination_path.exists() and skip_existing and not overwrite:
                record.status = "SKIPPED"
            else:
                shutil.copy2(media.path, destination_path)
                record.sha256_destination = calculate_sha256(destination_path)
                record.status = "SUCCESS" if record.sha256_destination == record.sha256_source else "FAILED"
                if record.status == "FAILED":
                    record.error = "SHA256 mismatch after transfer."
        except Exception as exc:  # noqa: BLE001
            record.status = "FAILED"
            record.error = str(exc)
        finally:
            record.duration_seconds = round(perf_counter() - started, 3)
        result.records.append(record)

    result.transfer_json_path, result.transfer_csv_path = write_transfer_report(result, output)
    return result


def write_transfer_report(result: PipelineSyncResult, output_dir: Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    json_path = output / "transfer_report.json"
    csv_path = output / "transfer_report.csv"
    json_path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=TRANSFER_FIELDS)
        writer.writeheader()
        for record in result.records:
            writer.writerow({field: record.to_dict().get(field, "") for field in TRANSFER_FIELDS})
    return json_path, csv_path

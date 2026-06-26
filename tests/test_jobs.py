import json
from pathlib import Path

from mediaqc.processing.jobs import ProcessingJob, run_jobs, write_job_report


def test_jobs_dry_run_and_report(tmp_path: Path) -> None:
    output = tmp_path / "out.mp4"
    job = ProcessingJob(
        input_path=tmp_path / "in.mov",
        output_path=output,
        preset="h264_preview",
        command=["ffmpeg", "-version"],
        log_path=tmp_path / "job.log",
    )

    jobs = run_jobs([job], dry_run=True)
    json_path, csv_path = write_job_report(jobs, tmp_path)

    assert jobs[0].status == "SUCCESS"
    assert jobs[0].result is not None
    assert jobs[0].result.dry_run is True
    assert json.loads(json_path.read_text(encoding="utf-8"))["total_jobs"] == 1
    assert "h264_preview" in csv_path.read_text(encoding="utf-8-sig")


def test_job_skip_existing(tmp_path: Path) -> None:
    output = tmp_path / "out.mp4"
    output.write_bytes(b"done")
    job = ProcessingJob(
        input_path=tmp_path / "in.mov",
        output_path=output,
        preset="h264_preview",
        command=["ffmpeg", "-version"],
        skip_existing=True,
    )

    jobs = run_jobs([job], dry_run=True)

    assert jobs[0].status == "SKIPPED"
    assert jobs[0].output_size_bytes == 4

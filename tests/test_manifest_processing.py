from pathlib import Path

from mediaqc.processing.transcode import build_transcode_jobs


def test_transcode_job_generation_preserves_structure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("mediaqc.processing.ffmpeg_runner.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr("mediaqc.processing.encoder_backends.get_available_encoders", lambda: {"libx264"})
    media = tmp_path / "Media" / "Scene" / "Opening.mov"
    media.parent.mkdir(parents=True)
    media.write_bytes(b"fake")

    jobs = build_transcode_jobs(
        tmp_path / "Media",
        tmp_path / "encoded",
        "h264_preview",
        recursive=True,
        preserve_structure=True,
        overwrite=True,
    )

    assert len(jobs) == 1
    assert jobs[0].output_path == tmp_path / "encoded" / "Scene" / "Opening_preview.mp4"
    assert jobs[0].command[0].endswith("ffmpeg") or jobs[0].command[0] == "ffmpeg"
    assert "libx264" in jobs[0].command

from pathlib import Path

import pytest

from mediaqc.processing.ffmpeg_runner import (
    FFmpegNotFoundError,
    build_doctor_report,
    run_command,
    run_ffmpeg,
)
from mediaqc.processing.ffplay import build_ffplay_args


def test_run_command_dry_run_does_not_execute(tmp_path: Path) -> None:
    log_path = tmp_path / "dry.log"

    result = run_command(["ffmpeg", "-version"], log_path=log_path, dry_run=True)

    assert result.dry_run is True
    assert result.returncode == 0
    assert result.command == ["ffmpeg", "-version"]
    assert "DRY RUN: True" in log_path.read_text(encoding="utf-8")


def test_run_ffmpeg_missing_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("mediaqc.processing.ffmpeg_runner.shutil.which", lambda _: None)

    with pytest.raises(FFmpegNotFoundError, match="ffmpeg was not found"):
        run_ffmpeg(["-version"], dry_run=True)


def test_ffplay_command_generation() -> None:
    args = build_ffplay_args(Path("Opening.mov"), loop=True, mute=True, start="00:01:20", scale=0.5, timecode=True)

    assert "-loop" in args
    assert "-an" in args
    assert "-ss" in args
    assert args[-1] == "Opening.mov"
    assert any("drawtext" in item for item in args)


def test_doctor_handles_missing_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("mediaqc.processing.ffmpeg_runner.shutil.which", lambda _: None)

    report = build_doctor_report()

    assert report.ffmpeg_path is None
    assert report.errors

import stat
import subprocess
import sys
from pathlib import Path

from mediaqc.processing.ffmpeg_runner import resolve_tool_path


def make_executable(path: Path) -> None:
    path.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_resolve_tool_path_prefers_explicit_env(monkeypatch, tmp_path: Path) -> None:
    ffmpeg = tmp_path / ("ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg")
    make_executable(ffmpeg)
    monkeypatch.setenv("MEDIAQC_FFMPEG_PATH", str(ffmpeg))

    result = resolve_tool_path("ffmpeg")

    assert result.path == str(ffmpeg)
    assert result.source == "MEDIAQC_FFMPEG_PATH"


def test_resolve_tool_path_uses_bundled_directory(monkeypatch, tmp_path: Path) -> None:
    ffprobe = tmp_path / ("ffprobe.exe" if sys.platform.startswith("win") else "ffprobe")
    make_executable(ffprobe)
    monkeypatch.delenv("MEDIAQC_FFPROBE_PATH", raising=False)
    monkeypatch.setenv("MEDIAQC_FFMPEG_DIR", str(tmp_path))

    result = resolve_tool_path("ffprobe")

    assert result.path == str(ffprobe)
    assert result.source == "MEDIAQC_FFMPEG_DIR"


def test_make_release_generates_assets(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    output = tmp_path / "dist_release"
    cli = dist / "loom-cli"
    gui = dist / "Loom"
    cli.mkdir(parents=True)
    gui.mkdir(parents=True)
    (cli / "mediaqc").write_text("cli", encoding="utf-8")
    (gui / "Loom").write_text("gui", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "packaging/scripts/make_release.py",
            "--platform",
            "test",
            "--dist",
            str(dist),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert any(path.name.startswith("loom-cli-") for path in output.glob("*.zip"))
    assert any(path.name.startswith("Loom-") for path in output.glob("*.zip"))
    assert (output / "SHA256SUMS.txt").read_text(encoding="utf-8")
    assert "CLI entry: `mediaqc`" in (output / "release_notes.md").read_text(encoding="utf-8")
    assert "GUI app: `Loom`" in (output / "release_notes.md").read_text(encoding="utf-8")

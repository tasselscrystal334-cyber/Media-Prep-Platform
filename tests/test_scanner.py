from pathlib import Path

import pytest

from mediaqc.scanner import scan_media_files


def test_scan_media_files_finds_supported_extensions_case_insensitive(tmp_path: Path) -> None:
    (tmp_path / "Opening.MOV").write_bytes(b"video")
    (tmp_path / "still.PNG").write_bytes(b"image")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    nested = tmp_path / "中文 文件夹"
    nested.mkdir()
    (nested / "voice.WAV").write_bytes(b"audio")

    results = scan_media_files(tmp_path)

    filenames = {item.filename for item in results}
    assert filenames == {"Opening.MOV", "still.PNG", "voice.WAV"}
    assert {item.extension for item in results} == {".mov", ".png", ".wav"}


def test_scan_media_files_rejects_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan_media_files(tmp_path / "missing")

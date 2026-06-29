"""Helpers for GUI source preview lists."""

from __future__ import annotations

from pathlib import Path

from mediaqc.scanner import is_supported_media


def list_preview_media_files(folder: Path, limit: int = 10) -> tuple[list[Path], int]:
    """Return supported top-level media files for source preview."""

    path = Path(folder)
    if not path.is_dir():
        return ([], 0)
    files = [item for item in sorted(path.iterdir(), key=lambda item: item.name.casefold()) if is_supported_media(item)]
    return (files[:limit], len(files))


def is_preview_media_file(path: Path) -> bool:
    """Return whether a path should be shown as a media source."""

    return is_supported_media(Path(path))

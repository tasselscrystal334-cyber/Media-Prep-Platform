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


def build_source_preview_lines(folder: Path, limit: int = 10) -> tuple[list[str], int]:
    """Build human-readable source preview text for a folder."""

    path = Path(folder)
    files, total_files = list_preview_media_files(path, limit=limit)
    lines = [f"Source folder: {path}", "", f"Files ({total_files} detected):"]
    if files:
        lines.extend(f"- {item.name}" for item in files)
    else:
        lines.append("No supported media files found.")
    if total_files > len(files):
        lines.append(f"... {total_files - len(files)} more")
    return (lines, total_files)

"""Helpers for GUI source preview lists."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mediaqc.scanner import is_supported_media


@dataclass(frozen=True)
class SourceTitle:
    index: int
    path: Path
    duration: str

    @property
    def label(self) -> str:
        return f"{self.index} - {self.duration} - {self.path.stem}"


def list_preview_media_files(folder: Path, limit: int = 10) -> tuple[list[Path], int]:
    """Return supported top-level media files for source preview."""

    path = Path(folder)
    if not path.is_dir():
        return ([], 0)
    files = [item for item in sorted(path.iterdir(), key=lambda item: item.name.casefold()) if is_supported_media(item)]
    return (files[:limit], len(files))


def list_source_titles(folder: Path, limit: int = 50) -> list[SourceTitle]:
    """Return title dropdown rows for supported top-level media files."""

    files, _ = list_preview_media_files(folder, limit=limit)
    return [
        SourceTitle(index=index, path=path, duration=probe_duration_label(path))
        for index, path in enumerate(files, start=1)
    ]


def probe_duration_label(path: Path) -> str:
    """Return HH:MM:SS duration for a media file, or a placeholder."""

    try:
        from mediaqc.probe import probe_media

        duration = probe_media(path).get("duration")
    except Exception:  # noqa: BLE001 - preview should remain usable without ffprobe.
        duration = None
    return format_duration(duration)


def format_duration(value: object) -> str:
    """Format ffprobe duration seconds as HH:MM:SS."""

    try:
        seconds = int(round(float(value)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "--:--:--"
    hours, remainder = divmod(max(seconds, 0), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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

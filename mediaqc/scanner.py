"""Filesystem scanner for supported media files."""

from __future__ import annotations

from pathlib import Path

from .models import MediaFileResult

VIDEO_EXTENSIONS = {".mov", ".mp4", ".mxf", ".avi", ".mkv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".exr"}
AUDIO_EXTENSIONS = {".wav", ".aiff", ".mp3"}
SUPPORTED_EXTENSIONS = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS | AUDIO_EXTENSIONS


def is_supported_media(path: Path) -> bool:
    """Return whether a path has a supported media extension."""

    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def scan_media_files(root: Path) -> list[MediaFileResult]:
    """Recursively scan a folder and return supported media files."""

    root = Path(root).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {root}")

    results: list[MediaFileResult] = []
    for path in sorted(root.rglob("*"), key=lambda item: str(item).casefold()):
        if not is_supported_media(path):
            continue

        try:
            size_bytes = path.stat().st_size
            result = MediaFileResult(
                path=path.resolve(),
                filename=path.name,
                extension=path.suffix.lower(),
                size_bytes=size_bytes,
            )
        except OSError as exc:
            result = MediaFileResult(
                path=path,
                filename=path.name,
                extension=path.suffix.lower(),
                size_bytes=0,
                status="FAIL",
                errors=[f"Unable to read file metadata: {exc}"],
            )
        results.append(result)

    return results

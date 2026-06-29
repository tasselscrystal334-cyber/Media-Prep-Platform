"""Live output preview helpers for the Loom desktop GUI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreviewSettings:
    source_path: Path | None
    preset: str
    output_format: str
    duration_seconds: int


def build_output_preview_text(settings: PreviewSettings) -> str:
    """Build a readable live preview summary for the selected output."""

    source = settings.source_path.name if settings.source_path else "No source selected"
    stem = settings.source_path.stem if settings.source_path else "untitled"
    extension = _format_extension(settings.output_format)
    output_name = f"{stem}{extension}" if stem else f"untitled{extension}"
    return "\n".join(
        [
            "Live Preview",
            "",
            f"Source: {source}",
            f"Preset: {settings.preset}",
            f"Format: {settings.output_format}",
            f"Duration: {settings.duration_seconds} sec",
            f"Output: {output_name}",
            "",
            "Preview status: ready",
        ]
    )


def _format_extension(output_format: str) -> str:
    mapping = {
        "MP4": ".mp4",
        "MOV": ".mov",
        "MKV": ".mkv",
        "WebM": ".webm",
        "MXF": ".mxf",
        "AVI": ".avi",
        "Image Sequence": "_frames",
    }
    return mapping.get(output_format, ".mp4")

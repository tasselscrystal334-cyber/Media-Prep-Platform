"""ffprobe integration."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


class FFprobeNotFoundError(RuntimeError):
    """Raised when ffprobe is unavailable."""


def ensure_ffprobe_available() -> str:
    """Return the ffprobe executable path, or raise a clear error."""

    executable = shutil.which("ffprobe")
    if executable is None:
        raise FFprobeNotFoundError(
            "ffprobe was not found. Install FFmpeg and make sure ffprobe is on PATH."
        )
    return executable


def probe_media(path: Path) -> dict[str, Any]:
    """Run ffprobe and return normalized JSON data."""

    executable = ensure_ffprobe_available()
    command = [
        executable,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(Path(path)),
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        raise RuntimeError(f"ffprobe failed with exit code {completed.returncode}: {stderr}")

    try:
        raw_data = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ffprobe returned invalid JSON: {exc}") from exc

    return normalize_ffprobe(raw_data)


def normalize_ffprobe(data: dict[str, Any]) -> dict[str, Any]:
    """Keep report-friendly ffprobe fields while preserving stream detail."""

    format_info = data.get("format") or {}
    streams = data.get("streams") or []

    normalized_streams: list[dict[str, Any]] = []
    for stream in streams:
        normalized_streams.append(
            {
                "codec_type": stream.get("codec_type"),
                "codec_name": stream.get("codec_name"),
                "width": stream.get("width"),
                "height": stream.get("height"),
                "avg_frame_rate": stream.get("avg_frame_rate"),
                "pix_fmt": stream.get("pix_fmt"),
                "color_space": stream.get("color_space"),
                "color_range": stream.get("color_range"),
                "sample_rate": stream.get("sample_rate"),
                "channels": stream.get("channels"),
                "channel_layout": stream.get("channel_layout"),
            }
        )

    return {
        "format_name": format_info.get("format_name"),
        "duration": format_info.get("duration"),
        "bit_rate": format_info.get("bit_rate"),
        "streams": normalized_streams,
    }

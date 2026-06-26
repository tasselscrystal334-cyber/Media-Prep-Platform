"""Subtitle embedding and burn-in command builders."""

from __future__ import annotations

from pathlib import Path

from .ffmpeg_runner import EncoderNotAvailableError, get_available_filters

SUBTITLE_EXTENSIONS = {".srt", ".ass", ".vtt"}


def build_subtitle_command(
    input_path: Path,
    subtitle_path: Path,
    output_path: Path,
    mode: str,
    fonts_dir: Path | None = None,
    overwrite: bool = False,
) -> list[str]:
    input_path = Path(input_path)
    subtitle_path = Path(subtitle_path)
    output_path = Path(output_path)
    if subtitle_path.suffix.lower() not in SUBTITLE_EXTENSIONS:
        raise ValueError("Subtitle file must be .srt, .ass, or .vtt.")
    args = ["ffmpeg", "-y" if overwrite else "-n", "-i", str(input_path)]
    if mode == "soft":
        args.extend(["-i", str(subtitle_path), "-c:v", "copy", "-c:a", "copy", "-c:s", _subtitle_codec(output_path)])
    elif mode == "burn":
        filter_value = _subtitle_filter(subtitle_path, fonts_dir)
        args.extend(["-vf", filter_value, "-c:a", "copy"])
    else:
        raise ValueError("Subtitle mode must be 'soft' or 'burn'.")
    args.append(str(output_path))
    return args


def ensure_subtitle_filter_available(filters: set[str] | None = None) -> None:
    available = filters if filters is not None else get_available_filters()
    if available and "subtitles" not in available:
        raise EncoderNotAvailableError("FFmpeg subtitles filter is not available in this build.")


def _subtitle_codec(output_path: Path) -> str:
    suffix = output_path.suffix.lower()
    if suffix == ".mp4":
        return "mov_text"
    if suffix == ".mov":
        return "text"
    if suffix == ".mkv":
        return "copy"
    return "mov_text"


def _subtitle_filter(subtitle_path: Path, fonts_dir: Path | None) -> str:
    escaped = _escape_filter_path(subtitle_path)
    if fonts_dir is None:
        return f"subtitles='{escaped}'"
    return f"subtitles='{escaped}':fontsdir='{_escape_filter_path(fonts_dir)}'"


def _escape_filter_path(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

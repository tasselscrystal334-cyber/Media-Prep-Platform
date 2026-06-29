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


@dataclass(frozen=True)
class PreviewBuild:
    output_path: Path
    ffmpeg_args: list[str]
    ffplay_args: list[str]


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
            "Preview status: preparing output video",
        ]
    )


def build_output_preview(
    settings: PreviewSettings,
    preview_dir: Path,
    max_width: int = 1280,
) -> PreviewBuild:
    """Build FFmpeg and FFplay arguments for a playable output preview clip."""

    if settings.source_path is None:
        raise ValueError("source_path is required for live output preview")

    preview_dir.mkdir(parents=True, exist_ok=True)
    output_path = preview_dir / f"{settings.source_path.stem}_loom_preview{_preview_extension(settings.output_format)}"
    video_args = _video_encoder_args(settings)
    audio_args = _audio_encoder_args(settings.output_format)
    ffmpeg_args = [
        "-y",
        "-hide_banner",
        "-ss",
        "0",
        "-t",
        str(max(1, settings.duration_seconds)),
        "-i",
        str(settings.source_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        f"scale='min({max_width},iw)':-2",
        *video_args,
        *audio_args,
        str(output_path),
    ]
    ffplay_args = [
        "-autoexit",
        "-window_title",
        "Loom Output Preview",
        str(output_path),
    ]
    return PreviewBuild(output_path=output_path, ffmpeg_args=ffmpeg_args, ffplay_args=ffplay_args)


def build_transcode_args(
    source_path: Path,
    output_path: Path,
    preset: str,
    output_format: str,
    fps: str = "Source FPS",
    crop_filter: str | None = None,
) -> list[str]:
    """Build FFmpeg arguments for a full output transcode."""

    settings = PreviewSettings(source_path=source_path, preset=preset, output_format=output_format, duration_seconds=0)
    filters: list[str] = []
    if crop_filter:
        filters.append(crop_filter)
    args = [
        "-y",
        "-hide_banner",
        "-i",
        str(source_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
    ]
    if filters:
        args.extend(["-vf", ",".join(filters)])
    args.extend(_video_encoder_args(settings))
    if fps != "Source FPS":
        args.extend(["-r", fps.replace(" fps", "")])
    args.extend(_audio_encoder_args(output_format))
    args.append(str(output_path))
    return args


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


def _preview_extension(output_format: str) -> str:
    if output_format == "Image Sequence":
        return ".mp4"
    return _format_extension(output_format)


def _video_encoder_args(settings: PreviewSettings) -> list[str]:
    preset = settings.preset.lower()
    output_format = settings.output_format.lower()
    if output_format == "webm":
        return ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34"]
    if "h.265" in preset or "h265" in preset or "hevc" in preset:
        return ["-c:v", "libx265", "-preset", "veryfast", "-crf", "28"]
    if "prores 4444" in preset:
        return ["-c:v", "prores_ks", "-profile:v", "4"]
    if "prores" in preset:
        return ["-c:v", "prores_ks", "-profile:v", "3"]
    if "hap q alpha" in preset:
        return ["-c:v", "hap", "-format", "hap_q_alpha"]
    if "hap alpha" in preset:
        return ["-c:v", "hap", "-format", "hap_alpha"]
    if "hap" in preset:
        return ["-c:v", "hap", "-format", "hap_q"]
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23"]


def _audio_encoder_args(output_format: str) -> list[str]:
    return ["-c:a", "copy"]

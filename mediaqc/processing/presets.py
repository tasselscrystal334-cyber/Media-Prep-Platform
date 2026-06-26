"""Transcode preset loading and FFmpeg argument generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .ffmpeg_runner import EncoderNotAvailableError, get_available_encoders

PRESET_DIR = Path(__file__).resolve().parents[2] / "config" / "transcode_presets"


@dataclass(slots=True)
class TranscodePreset:
    key: str
    path: Path
    data: dict[str, Any]

    @property
    def name(self) -> str:
        return str(self.data.get("name") or self.key)

    @property
    def video_codec(self) -> str:
        return str((self.data.get("video") or {}).get("codec") or "")

    @property
    def output_suffix(self) -> str:
        return str((self.data.get("output") or {}).get("suffix") or f"_{self.key}")

    @property
    def output_extension(self) -> str:
        return str((self.data.get("output") or {}).get("extension") or ".mov")


def load_preset(name_or_path: str | Path, preset_dir: Path | None = None) -> TranscodePreset:
    path = Path(name_or_path)
    if path.suffix.lower() not in {".yaml", ".yml"}:
        path = (preset_dir or PRESET_DIR) / f"{name_or_path}.yaml"
    path = path.expanduser()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Preset must be a YAML mapping: {path}")
    preset = TranscodePreset(key=path.stem, path=path, data=raw)
    validate_preset(preset)
    return preset


def validate_preset(preset: TranscodePreset) -> None:
    data = preset.data
    if not data.get("name"):
        raise ValueError("Preset requires a name.")
    if not isinstance(data.get("video"), dict) or not data["video"].get("codec"):
        raise ValueError("Preset requires video.codec.")
    if not isinstance(data.get("output"), dict) or not data["output"].get("extension"):
        raise ValueError("Preset requires output.extension.")


def ensure_preset_encoder_available(preset: TranscodePreset, encoders: set[str] | None = None) -> None:
    codec = preset.video_codec
    if codec == "notchlc":
        raise EncoderNotAvailableError(
            "NotchLC encoder backend is not available. Please configure config/encoder_backends.yaml or use another preset."
        )
    available = encoders if encoders is not None else get_available_encoders()
    if available and codec not in available:
        raise EncoderNotAvailableError(f"Encoder '{codec}' is not available in this FFmpeg build.")


def build_output_path(input_path: Path, output_dir: Path, preset: TranscodePreset, root: Path | None = None) -> Path:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    if root is not None:
        try:
            relative_parent = input_path.parent.resolve().relative_to(Path(root).resolve())
        except ValueError:
            relative_parent = Path()
        output_dir = output_dir / relative_parent
    return output_dir / f"{input_path.stem}{preset.output_suffix}{preset.output_extension}"


def build_ffmpeg_args(input_path: Path, output_path: Path, preset: TranscodePreset, overwrite: bool = False) -> list[str]:
    video = preset.data.get("video") or {}
    audio = preset.data.get("audio") or {}
    args = ["-y" if overwrite else "-n", "-i", str(Path(input_path))]

    filters = _video_filters(video)
    if filters:
        args.extend(["-vf", ",".join(filters)])

    args.extend(["-c:v", str(video["codec"])])
    if video.get("format"):
        args.extend(["-format", str(video["format"])])
    if video.get("pix_fmt"):
        args.extend(["-pix_fmt", str(video["pix_fmt"])])
    if video.get("fps") not in (None, "source"):
        args.extend(["-r", str(video["fps"])])
    if video.get("profile"):
        args.extend(["-profile:v", str(video["profile"])])
    if video.get("crf") is not None:
        args.extend(["-crf", str(video["crf"])])
    if video.get("preset"):
        args.extend(["-preset", str(video["preset"])])
    args.extend(str(item) for item in video.get("extra_args") or [])

    audio_mode = audio.get("mode")
    if audio_mode == "none":
        args.append("-an")
    elif audio_mode == "copy":
        args.extend(["-c:a", "copy"])
    elif audio.get("codec"):
        args.extend(["-c:a", str(audio["codec"])])
        if audio.get("bitrate"):
            args.extend(["-b:a", str(audio["bitrate"])])

    args.append(str(Path(output_path)))
    return args


def _video_filters(video: dict[str, Any]) -> list[str]:
    filters: list[str] = []
    scale = video.get("scale") or {}
    width = scale.get("width")
    height = scale.get("height")
    max_width = video.get("max_width")
    if width and height and width != "source" and height != "source":
        filters.append(f"scale={width}:{height}")
    elif max_width:
        filters.append(f"scale='min({max_width},iw)':-2")
    return filters

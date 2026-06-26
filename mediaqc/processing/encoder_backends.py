"""Optional encoder backend support."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .ffmpeg_runner import EncoderNotAvailableError, check_ffmpeg_available, get_available_encoders
from .presets import TranscodePreset, build_ffmpeg_args

BACKENDS_CONFIG = Path(__file__).resolve().parents[2] / "config" / "encoder_backends.yaml"


class EncoderBackend:
    name = "base"

    def supports(self, codec_name: str) -> bool:
        raise NotImplementedError

    def check_available(self) -> bool:
        raise NotImplementedError

    def build_command(
        self,
        input_path: Path,
        output_path: Path,
        preset: TranscodePreset,
        options: dict[str, Any] | None = None,
    ) -> list[str]:
        raise NotImplementedError


class FFmpegBackend(EncoderBackend):
    name = "ffmpeg"

    def supports(self, codec_name: str) -> bool:
        return codec_name != "notchlc"

    def check_available(self) -> bool:
        check_ffmpeg_available()
        return True

    def build_command(
        self,
        input_path: Path,
        output_path: Path,
        preset: TranscodePreset,
        options: dict[str, Any] | None = None,
    ) -> list[str]:
        options = options or {}
        return [check_ffmpeg_available(), *build_ffmpeg_args(input_path, output_path, preset, bool(options.get("overwrite")))]


@dataclass(slots=True)
class NotchLCExternalBackend(EncoderBackend):
    config: dict[str, Any]
    name: str = "notchlc_external"

    def supports(self, codec_name: str) -> bool:
        return codec_name == "notchlc"

    def check_available(self) -> bool:
        executable = self.config.get("executable_path")
        return bool(self.config.get("enabled") and executable and Path(executable).exists())

    def build_command(
        self,
        input_path: Path,
        output_path: Path,
        preset: TranscodePreset,
        options: dict[str, Any] | None = None,
    ) -> list[str]:
        if not self.check_available():
            raise EncoderNotAvailableError(
                "NotchLC encoder backend is not available. Please configure config/encoder_backends.yaml or use another preset."
            )
        quality = (options or {}).get("quality") or self.config.get("default_quality") or "high"
        return [
            str(self.config["executable_path"]),
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "--quality",
            str(quality),
            *[str(item) for item in self.config.get("extra_args") or []],
        ]


@dataclass(slots=True)
class CustomCommandBackend(EncoderBackend):
    codec_name: str
    config: dict[str, Any]
    name: str = "custom_command"

    def supports(self, codec_name: str) -> bool:
        return codec_name == self.codec_name

    def check_available(self) -> bool:
        if not self.config.get("enabled"):
            return False
        encoder_path = self.config.get("encoder_path")
        return bool(encoder_path and (Path(encoder_path).exists() or shutil.which(str(encoder_path))))

    def build_command(
        self,
        input_path: Path,
        output_path: Path,
        preset: TranscodePreset,
        options: dict[str, Any] | None = None,
    ) -> list[str]:
        if not self.check_available():
            raise EncoderNotAvailableError(
                "NotchLC encoder backend is not available. Please configure config/encoder_backends.yaml or use another preset."
            )
        values = {
            "encoder_path": self.config.get("encoder_path", ""),
            "input": str(input_path),
            "output": str(output_path),
            "quality": (options or {}).get("quality") or self.config.get("quality") or "high",
        }
        return [str(part).format(**values) for part in self.config.get("command_template") or []]


def load_backend_config(path: Path | None = None) -> dict[str, Any]:
    config_path = Path(path or BACKENDS_CONFIG)
    if not config_path.exists():
        return {}
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("Encoder backend config must be a YAML mapping.")
    return raw


def available_backends(config_path: Path | None = None) -> list[EncoderBackend]:
    config = load_backend_config(config_path)
    backends: list[EncoderBackend] = [FFmpegBackend()]
    if isinstance(config.get("notchlc"), dict):
        backends.append(NotchLCExternalBackend(config["notchlc"]))
    custom = config.get("custom") or {}
    for codec_name, item in custom.items():
        if isinstance(item, dict):
            backends.append(CustomCommandBackend(codec_name=codec_name, config=item))
    return backends


def select_backend(preset: TranscodePreset, config_path: Path | None = None) -> EncoderBackend:
    codec = preset.video_codec
    for backend in available_backends(config_path):
        if backend.supports(codec) and backend.check_available():
            if isinstance(backend, FFmpegBackend):
                encoders = get_available_encoders()
                if encoders and codec not in encoders:
                    continue
            return backend
    if codec == "notchlc":
        raise EncoderNotAvailableError(
            "NotchLC encoder backend is not available. Please configure config/encoder_backends.yaml or use another preset."
        )
    raise EncoderNotAvailableError(f"Encoder backend for '{codec}' is not available.")

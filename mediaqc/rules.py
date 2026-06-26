"""Project rule loading and evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import MediaFileResult


@dataclass(slots=True)
class VideoRules:
    allowed_codecs: list[str] = field(default_factory=list)
    expected_width: int | None = None
    expected_height: int | None = None
    expected_fps: float | None = None
    allowed_pix_fmt: list[str] = field(default_factory=list)
    expected_color_space: str | None = None
    expected_bit_depth: int | None = None
    min_bit_rate: int | None = None
    max_bit_rate: int | None = None


@dataclass(slots=True)
class AudioRules:
    allow_audio: bool = True


@dataclass(slots=True)
class FileRules:
    min_size_bytes: int | None = None
    max_size_bytes: int | None = None


@dataclass(slots=True)
class FilenameRules:
    required_pattern: str | None = None
    forbidden_pattern: str | None = None


@dataclass(slots=True)
class FolderRules:
    required_path_patterns: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectRules:
    project_name: str | None = None
    profile_name: str | None = None
    video: VideoRules = field(default_factory=VideoRules)
    audio: AudioRules = field(default_factory=AudioRules)
    file: FileRules = field(default_factory=FileRules)
    filename: FilenameRules = field(default_factory=FilenameRules)
    folder: FolderRules = field(default_factory=FolderRules)
    validators: dict[str, bool] = field(default_factory=dict)


def load_rules(path: Path) -> ProjectRules:
    """Load project rules from a YAML file."""

    rules_path = Path(path).expanduser()
    try:
        raw = yaml.safe_load(rules_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML rules file: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Rules file must contain a YAML mapping at the top level.")

    video_raw = _mapping(raw.get("video"), "video")
    audio_raw = _mapping(raw.get("audio"), "audio")
    file_raw = _mapping(raw.get("file"), "file")
    filename_raw = _mapping(raw.get("filename"), "filename")
    folder_raw = _mapping(raw.get("folder"), "folder")
    validators_raw = _mapping(raw.get("validators"), "validators")

    return ProjectRules(
        project_name=_optional_str(raw.get("project_name")),
        profile_name=_optional_str(raw.get("profile_name")),
        video=VideoRules(
            allowed_codecs=_str_list(video_raw.get("allowed_codecs")),
            expected_width=_optional_int(video_raw.get("expected_width"), "video.expected_width"),
            expected_height=_optional_int(video_raw.get("expected_height"), "video.expected_height"),
            expected_fps=_optional_float(video_raw.get("expected_fps"), "video.expected_fps"),
            allowed_pix_fmt=_str_list(video_raw.get("allowed_pix_fmt")),
            expected_color_space=_optional_str(video_raw.get("expected_color_space")),
            expected_bit_depth=_optional_int(video_raw.get("expected_bit_depth"), "video.expected_bit_depth"),
            min_bit_rate=_optional_int(video_raw.get("min_bit_rate"), "video.min_bit_rate"),
            max_bit_rate=_optional_int(video_raw.get("max_bit_rate"), "video.max_bit_rate"),
        ),
        audio=AudioRules(
            allow_audio=bool(audio_raw.get("allow_audio", True)),
        ),
        file=FileRules(
            min_size_bytes=_optional_int(file_raw.get("min_size_bytes"), "file.min_size_bytes"),
            max_size_bytes=_optional_int(file_raw.get("max_size_bytes"), "file.max_size_bytes"),
        ),
        filename=FilenameRules(
            required_pattern=_optional_str(filename_raw.get("required_pattern")),
            forbidden_pattern=_optional_str(filename_raw.get("forbidden_pattern")),
        ),
        folder=FolderRules(
            required_path_patterns=_str_list(folder_raw.get("required_path_patterns")),
        ),
        validators={str(key): bool(value) for key, value in validators_raw.items()},
    )


def evaluate_rules(item: MediaFileResult, rules: ProjectRules) -> None:
    """Populate rule_status, warnings, and failures for a media result."""

    from .validation_engine import ValidationEngine

    ValidationEngine(rules).apply(item)


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Rules section '{name}' must be a mapping.")
    return value


def _optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Rules field '{field_name}' must be an integer.") from exc


def _optional_float(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Rules field '{field_name}' must be a number.") from exc


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        raise ValueError("Rules list fields must be YAML lists or strings.")
    return [str(item) for item in value]

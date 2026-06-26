"""Validation plugin API and registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

if False:  # pragma: no cover
    from mediaqc.models import MediaFileResult
    from mediaqc.rules import ProjectRules


@dataclass(slots=True)
class ValidationResult:
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    validator: str = ""
    severity: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "validator": self.validator,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
        }


class BaseValidator:
    name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    severity: ClassVar[str] = "FAIL"

    def __init__(self, rules: "ProjectRules") -> None:
        self.rules = rules

    def validate(self, media: "MediaFileResult") -> ValidationResult:
        raise NotImplementedError

    def result(
        self,
        status: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> ValidationResult:
        return ValidationResult(
            status=status,
            message=message,
            details=details or {},
            validator=self.name,
            severity=self.severity,
        )


VALIDATOR_REGISTRY: dict[str, type[BaseValidator]] = {}


def register_validator(validator_cls: type[BaseValidator]) -> type[BaseValidator]:
    """Register a validator class for built-ins or external plugins."""

    if not validator_cls.name:
        raise ValueError("Validator classes must define a non-empty name.")
    VALIDATOR_REGISTRY[validator_cls.name] = validator_cls
    return validator_cls


def get_video_stream(media: "MediaFileResult") -> dict[str, Any]:
    return _first_stream(media, "video")


def get_audio_stream(media: "MediaFileResult") -> dict[str, Any]:
    return _first_stream(media, "audio")


def has_video_expectations(rules: "ProjectRules") -> bool:
    return any(
        [
            rules.video.allowed_codecs,
            rules.video.expected_width is not None,
            rules.video.expected_height is not None,
            rules.video.expected_fps is not None,
            rules.video.allowed_pix_fmt,
            rules.video.expected_color_space,
            rules.video.expected_bit_depth is not None,
            rules.video.min_bit_rate is not None,
            rules.video.max_bit_rate is not None,
        ]
    )


def parse_bit_rate(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def lower(value: Any) -> str:
    return str(value).casefold() if value is not None else ""


def _first_stream(media: "MediaFileResult", codec_type: str) -> dict[str, Any]:
    ffprobe = media.ffprobe or {}
    for stream in ffprobe.get("streams", []):
        if stream.get("codec_type") == codec_type:
            return stream
    return {}

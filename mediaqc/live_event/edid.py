"""Project output specification checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class OutputCheck:
    status: str = "PASS"
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "warnings": self.warnings,
            "failures": self.failures,
            "details": self.details,
        }


def load_output_spec(path: Path) -> dict[str, Any]:
    spec_path = Path(path).expanduser()
    raw = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("Output spec must be a YAML mapping.")
    output = raw.get("output")
    if not isinstance(output, dict):
        raise ValueError("Output spec requires an 'output' mapping.")
    return raw


def check_output_spec(media: Any, spec: dict[str, Any]) -> OutputCheck:
    output = spec.get("output") or {}
    video = _video_stream(media)
    check = OutputCheck(
        details={
            "project_name": spec.get("project_name"),
            "output_name": output.get("name"),
            "target_width": output.get("target_width"),
            "target_height": output.get("target_height"),
            "refresh_rate": output.get("refresh_rate"),
            "color_space": output.get("color_space"),
            "color_range": output.get("color_range"),
            "bit_depth": output.get("bit_depth"),
            "expected_inputs": output.get("expected_inputs", []),
        }
    )
    if not video:
        check.warnings.append("No video stream found for output spec comparison.")
        return _finalize(check)

    width = video.get("width")
    height = video.get("height")
    fps = _fps(video.get("avg_frame_rate"))
    color_space = video.get("color_space")
    color_range = video.get("color_range")

    check.details.update(
        {
            "media_width": width,
            "media_height": height,
            "media_fps": fps,
            "media_color_space": color_space,
            "media_color_range": color_range,
        }
    )

    if width != output.get("target_width") or height != output.get("target_height"):
        check.warnings.append(
            f"Media resolution {width}x{height} does not match output canvas "
            f"{output.get('target_width')}x{output.get('target_height')}."
        )
    if output.get("refresh_rate") is not None and fps is not None:
        if abs(float(output["refresh_rate"]) - fps) > 0.01:
            check.warnings.append(f"Media FPS {fps:g} does not match output refresh {output['refresh_rate']}.")
    if output.get("color_space") and str(color_space).casefold() != str(output["color_space"]).casefold():
        check.warnings.append(f"Media color space '{color_space}' does not match '{output['color_space']}'.")
    if output.get("color_range") and color_range:
        expected_range = _normalize_range(output["color_range"])
        actual_range = _normalize_range(color_range)
        if actual_range != expected_range:
            check.warnings.append(f"Media color range '{color_range}' does not match '{output['color_range']}'.")

    return _finalize(check)


def summarize_output_spec(spec: dict[str, Any] | None, checks: list[OutputCheck]) -> dict[str, Any] | None:
    if spec is None:
        return None
    return {
        "spec": spec,
        "pass": sum(1 for item in checks if item.status == "PASS"),
        "warn": sum(1 for item in checks if item.status == "WARN"),
        "fail": sum(1 for item in checks if item.status == "FAIL"),
    }


def _video_stream(media: Any) -> dict[str, Any]:
    for stream in (getattr(media, "ffprobe", None) or {}).get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return {}


def _fps(value: Any) -> float | None:
    if value in (None, "", "0/0"):
        return None
    try:
        if isinstance(value, str) and "/" in value:
            return float(Fraction(value))
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _normalize_range(value: Any) -> str:
    normalized = str(value).casefold()
    return {"full": "pc", "limited": "tv"}.get(normalized, normalized)


def _finalize(check: OutputCheck) -> OutputCheck:
    if check.failures:
        check.status = "FAIL"
    elif check.warnings:
        check.status = "WARN"
    else:
        check.status = "PASS"
    return check

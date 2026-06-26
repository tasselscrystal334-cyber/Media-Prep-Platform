"""Video frame-rate validator."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from . import BaseValidator, get_video_stream, has_video_expectations, register_validator


@register_validator
class FrameRateValidator(BaseValidator):
    name = "framerate"
    description = "Validate video frame rate."
    severity = "FAIL"

    def validate(self, media):
        expected_fps = self.rules.video.expected_fps
        if expected_fps is None:
            return self.result("PASS", "No frame-rate rule configured.")

        video = get_video_stream(media)
        if not video and has_video_expectations(self.rules):
            return self.result("FAIL", "Expected video stream, but no video stream was found.")

        fps_raw = video.get("avg_frame_rate")
        fps = _fps_to_float(fps_raw)
        if fps is None:
            return self.result("FAIL", "Frame rate is missing or invalid.", {"actual": fps_raw})
        if abs(fps - expected_fps) > 0.01:
            return self.result(
                "FAIL",
                f"FPS is {fps:g}; expected {expected_fps:g}.",
                {"actual": fps, "expected": expected_fps, "raw": fps_raw},
            )
        return self.result("PASS", f"FPS is {fps:g}.", {"actual": fps, "raw": fps_raw})


def _fps_to_float(value: Any) -> float | None:
    if value in (None, "", "0/0"):
        return None
    try:
        if isinstance(value, str) and "/" in value:
            return float(Fraction(value))
        return float(value)
    except (ValueError, ZeroDivisionError):
        return None

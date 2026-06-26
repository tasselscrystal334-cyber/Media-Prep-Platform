"""Video color-space validator."""

from __future__ import annotations

from . import BaseValidator, get_video_stream, has_video_expectations, lower, register_validator


@register_validator
class ColorSpaceValidator(BaseValidator):
    name = "colorspace"
    description = "Validate video color space."
    severity = "FAIL"

    def validate(self, media):
        expected = self.rules.video.expected_color_space
        if not expected:
            return self.result("PASS", "No color-space rule configured.")

        video = get_video_stream(media)
        if not video and has_video_expectations(self.rules):
            return self.result("FAIL", "Expected video stream, but no video stream was found.")

        actual = video.get("color_space")
        if lower(actual) != lower(expected):
            return self.result(
                "FAIL",
                f"Color space is '{actual}'; expected '{expected}'.",
                {"actual": actual, "expected": expected},
            )
        return self.result("PASS", f"Color space is '{actual}'.", {"actual": actual})

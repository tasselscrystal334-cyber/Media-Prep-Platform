"""Video pixel-format validator."""

from __future__ import annotations

from . import BaseValidator, get_video_stream, has_video_expectations, lower, register_validator


@register_validator
class PixelFormatValidator(BaseValidator):
    name = "pixfmt"
    description = "Validate video pixel format."
    severity = "FAIL"

    def validate(self, media):
        allowed = self.rules.video.allowed_pix_fmt
        expected_bit_depth = self.rules.video.expected_bit_depth
        if not allowed and expected_bit_depth is None:
            return self.result("PASS", "No pixel-format rule configured.")

        video = get_video_stream(media)
        if not video and has_video_expectations(self.rules):
            return self.result("FAIL", "Expected video stream, but no video stream was found.")

        actual = video.get("pix_fmt")
        bit_depth = _infer_bit_depth(actual)
        if expected_bit_depth is not None and bit_depth != expected_bit_depth:
            return self.result(
                "FAIL",
                f"Pixel format '{actual}' appears to be {bit_depth}-bit; expected {expected_bit_depth}-bit.",
                {"actual": actual, "actual_bit_depth": bit_depth, "expected_bit_depth": expected_bit_depth},
            )
        allowed_normalized = {lower(value) for value in allowed}
        if allowed and lower(actual) not in allowed_normalized:
            return self.result(
                "FAIL",
                f"Pixel format '{actual}' is not allowed; expected one of: {', '.join(allowed)}.",
                {"actual": actual, "allowed": allowed},
            )
        return self.result(
            "PASS",
            f"Pixel format '{actual}' passed.",
            {"actual": actual, "bit_depth": bit_depth},
        )


def _infer_bit_depth(pix_fmt):
    value = lower(pix_fmt)
    if not value:
        return None
    if any(token in value for token in ("12", "p12")):
        return 12
    if any(token in value for token in ("10", "p10")):
        return 10
    if any(token in value for token in ("16", "p16")):
        return 16
    return 8

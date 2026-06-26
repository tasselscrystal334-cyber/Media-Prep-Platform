"""Video resolution validator."""

from __future__ import annotations

from . import BaseValidator, get_video_stream, has_video_expectations, register_validator


@register_validator
class ResolutionValidator(BaseValidator):
    name = "resolution"
    description = "Validate video width and height."
    severity = "FAIL"

    def validate(self, media):
        expected_width = self.rules.video.expected_width
        expected_height = self.rules.video.expected_height
        if expected_width is None and expected_height is None:
            return self.result("PASS", "No resolution rule configured.")

        video = get_video_stream(media)
        if not video and has_video_expectations(self.rules):
            return self.result("FAIL", "Expected video stream, but no video stream was found.")

        failures = []
        width = video.get("width")
        height = video.get("height")
        if expected_width is not None and width != expected_width:
            failures.append(f"Width is {width}; expected {expected_width}.")
        if expected_height is not None and height != expected_height:
            failures.append(f"Height is {height}; expected {expected_height}.")
        if failures:
            return self.result(
                "FAIL",
                " ".join(failures),
                {
                    "actual_width": width,
                    "actual_height": height,
                    "expected_width": expected_width,
                    "expected_height": expected_height,
                },
            )
        return self.result(
            "PASS",
            f"Resolution is {width}x{height}.",
            {"actual_width": width, "actual_height": height},
        )

"""Video codec validator."""

from __future__ import annotations

from . import BaseValidator, get_video_stream, has_video_expectations, lower, register_validator


@register_validator
class CodecValidator(BaseValidator):
    name = "codec"
    description = "Validate video codec against allowed codecs."
    severity = "FAIL"

    def validate(self, media):
        allowed = self.rules.video.allowed_codecs
        if not allowed:
            return self.result("PASS", "No codec rule configured.")

        video = get_video_stream(media)
        if not video and has_video_expectations(self.rules):
            return self.result("FAIL", "Expected video stream, but no video stream was found.")

        codec = video.get("codec_name")
        allowed_normalized = {lower(value) for value in allowed}
        if lower(codec) not in allowed_normalized:
            return self.result(
                "FAIL",
                f"Video codec '{codec}' is not allowed; expected one of: {', '.join(allowed)}.",
                {"actual": codec, "allowed": allowed},
            )
        return self.result("PASS", f"Video codec '{codec}' is allowed.", {"actual": codec})

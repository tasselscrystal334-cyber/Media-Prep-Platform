"""Media bit-rate validator."""

from __future__ import annotations

from . import BaseValidator, parse_bit_rate, register_validator


@register_validator
class BitRateValidator(BaseValidator):
    name = "bitrate"
    description = "Validate container bit rate."
    severity = "WARN"

    def validate(self, media):
        min_bit_rate = self.rules.video.min_bit_rate
        max_bit_rate = self.rules.video.max_bit_rate
        if min_bit_rate is None and max_bit_rate is None:
            return self.result("PASS", "No bit-rate rule configured.")

        ffprobe = media.ffprobe or {}
        actual = parse_bit_rate(ffprobe.get("bit_rate"))
        if actual is None:
            return self.result("WARN", "Bit rate is missing or invalid.")
        if min_bit_rate is not None and actual < min_bit_rate:
            return self.result(
                "WARN",
                f"Bit rate is {actual}; below minimum {min_bit_rate}.",
                {"actual": actual, "min": min_bit_rate},
            )
        if max_bit_rate is not None and actual > max_bit_rate:
            return self.result(
                "WARN",
                f"Bit rate is {actual}; above maximum {max_bit_rate}.",
                {"actual": actual, "max": max_bit_rate},
            )
        return self.result("PASS", f"Bit rate is {actual}.", {"actual": actual})

"""File-size validator."""

from __future__ import annotations

from . import BaseValidator, register_validator


@register_validator
class FileSizeValidator(BaseValidator):
    name = "filesize"
    description = "Validate file size boundaries."
    severity = "WARN"

    def validate(self, media):
        min_size = self.rules.file.min_size_bytes
        max_size = self.rules.file.max_size_bytes
        if min_size is None and max_size is None:
            return self.result("PASS", "No file-size rule configured.")

        actual = media.size_bytes
        if min_size is not None and actual < min_size:
            return self.result(
                "WARN",
                f"File size is {actual} bytes; below minimum {min_size}.",
                {"actual": actual, "min": min_size},
            )
        if max_size is not None and actual > max_size:
            return self.result(
                "WARN",
                f"File size is {actual} bytes; above maximum {max_size}.",
                {"actual": actual, "max": max_size},
            )
        return self.result("PASS", f"File size is {actual} bytes.", {"actual": actual})

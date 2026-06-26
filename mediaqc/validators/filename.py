"""Filename validator."""

from __future__ import annotations

import re

from . import BaseValidator, register_validator


@register_validator
class FilenameValidator(BaseValidator):
    name = "filename"
    description = "Validate filename patterns."
    severity = "WARN"

    def validate(self, media):
        required = self.rules.filename.required_pattern
        forbidden = self.rules.filename.forbidden_pattern
        if not required and not forbidden:
            return self.result("PASS", "No filename rule configured.")

        filename = media.filename
        if required and re.search(required, filename) is None:
            return self.result(
                "WARN",
                f"Filename '{filename}' does not match required pattern '{required}'.",
                {"filename": filename, "required_pattern": required},
            )
        if forbidden and re.search(forbidden, filename) is not None:
            return self.result(
                "WARN",
                f"Filename '{filename}' matches forbidden pattern '{forbidden}'.",
                {"filename": filename, "forbidden_pattern": forbidden},
            )
        return self.result("PASS", f"Filename '{filename}' passed.", {"filename": filename})

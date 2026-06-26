"""Folder structure validator."""

from __future__ import annotations

import re

from . import BaseValidator, register_validator


@register_validator
class FolderStructureValidator(BaseValidator):
    name = "folder_structure"
    description = "Validate media path against project folder structure hints."
    severity = "WARN"

    def validate(self, media):
        patterns = self.rules.folder.required_path_patterns
        if not patterns:
            return self.result("PASS", "No folder-structure rule configured.")

        path_text = str(media.path)
        if not any(re.search(pattern, path_text) for pattern in patterns):
            return self.result(
                "WARN",
                "File path does not match the recommended folder structure.",
                {"path": path_text, "required_path_patterns": patterns},
            )
        return self.result("PASS", "Folder structure passed.", {"path": path_text})

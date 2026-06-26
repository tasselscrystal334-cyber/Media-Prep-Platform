"""Project integrity verification against manifest files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mediaqc.hash_check import calculate_sha256
from mediaqc.scanner import scan_media_files


@dataclass(slots=True)
class IntegrityReport:
    status: str = "PASS"
    missing_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    new_files: list[str] = field(default_factory=list)
    duplicate_files: list[dict[str, Any]] = field(default_factory=list)
    empty_files: list[str] = field(default_factory=list)
    naming_warnings: list[str] = field(default_factory=list)
    offline_references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "missing_files": self.missing_files,
            "modified_files": self.modified_files,
            "new_files": self.new_files,
            "duplicate_files": self.duplicate_files,
            "empty_files": self.empty_files,
            "naming_warnings": self.naming_warnings,
            "offline_references": self.offline_references,
        }


def verify_manifest(project_path: Path, manifest_path: Path) -> IntegrityReport:
    root = Path(project_path).resolve()
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    report = IntegrityReport()
    expected = {item["relative_path"]: item for item in manifest.get("files", [])}
    actual_files = scan_media_files(root)
    actual = {str(Path(media.path).resolve().relative_to(root)): media for media in actual_files}

    for relative_path, item in expected.items():
        path = root / relative_path
        if not path.exists():
            report.missing_files.append(relative_path)
            continue
        if path.stat().st_size == 0:
            report.empty_files.append(relative_path)
        if item.get("size_bytes") is not None and path.stat().st_size != item.get("size_bytes"):
            report.modified_files.append(f"{relative_path}: size mismatch")
            continue
        if item.get("sha256"):
            sha256 = calculate_sha256(path)
            if sha256 != item.get("sha256"):
                report.modified_files.append(f"{relative_path}: sha256 mismatch")

    for relative_path, media in actual.items():
        if relative_path not in expected:
            report.new_files.append(relative_path)
        if media.size_bytes == 0:
            report.empty_files.append(relative_path)
        warning = _naming_warning(relative_path)
        if warning:
            report.naming_warnings.append(warning)

    hashes: dict[str, list[str]] = {}
    for media in actual_files:
        if media.size_bytes == 0:
            continue
        try:
            sha256 = calculate_sha256(media.path)
        except OSError:
            continue
        hashes.setdefault(sha256, []).append(str(Path(media.path).resolve().relative_to(root)))
    report.duplicate_files = [
        {"sha256": sha256, "paths": paths}
        for sha256, paths in hashes.items()
        if len(paths) > 1
    ]

    report.offline_references = [
        reference for reference in manifest.get("references", []) if not (root / reference).exists()
    ]
    return _finalize(report)


def _naming_warning(relative_path: str) -> str | None:
    if re.search(r"[\u4e00-\u9fff\s]", relative_path):
        return f"{relative_path}: contains Chinese characters or spaces"
    if re.search(r"[#%&?]", relative_path):
        return f"{relative_path}: contains risky special characters"
    if len(relative_path) > 180:
        return f"{relative_path}: path is very long"
    return None


def _finalize(report: IntegrityReport) -> IntegrityReport:
    if report.missing_files or report.modified_files or report.empty_files:
        report.status = "FAIL"
    elif report.new_files or report.duplicate_files or report.naming_warnings or report.offline_references:
        report.status = "WARN"
    else:
        report.status = "PASS"
    return report

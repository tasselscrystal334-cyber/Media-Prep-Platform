"""Shared data models for mediaqc."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MediaFileResult:
    """QC result for one media file."""

    path: Path
    filename: str
    extension: str
    size_bytes: int
    sha256: str | None = None
    hash_cached: bool = False
    status: str = "PASS"
    errors: list[str] = field(default_factory=list)
    ffprobe: dict[str, Any] | None = None
    rule_status: str = "PASS"
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    validation_results: list[Any] = field(default_factory=list)
    decode_report: Any | None = None
    output_match: Any | None = None
    canvas_match: Any | None = None
    codec_profile: Any | None = None
    manifest_status: str | None = None
    integrity_status: str | None = None

    def fail(self, message: str) -> None:
        self.status = "FAIL"
        self.errors.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "filename": self.filename,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "hash_cached": self.hash_cached,
            "status": self.status,
            "errors": self.errors,
            "ffprobe": self.ffprobe,
            "rule_status": self.rule_status,
            "warnings": self.warnings,
            "failures": self.failures,
            "validation_results": [
                result.to_dict() if hasattr(result, "to_dict") else result
                for result in self.validation_results
            ],
            "decode_report": (
                self.decode_report.to_dict()
                if hasattr(self.decode_report, "to_dict")
                else self.decode_report
            ),
            "output_match": _serializable(self.output_match),
            "canvas_match": _serializable(self.canvas_match),
            "codec_profile": _serializable(self.codec_profile),
            "codec_risk_level": getattr(self.codec_profile, "risk_level", None)
            if self.codec_profile is not None
            else None,
            "realtime_score": getattr(self.codec_profile, "realtime_score", None)
            if self.codec_profile is not None
            else None,
            "manifest_status": self.manifest_status,
            "integrity_status": self.integrity_status,
        }


def _serializable(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value

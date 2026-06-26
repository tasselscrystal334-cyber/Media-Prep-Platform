"""JSON, CSV, and HTML report writers."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from .models import MediaFileResult

CSV_FIELDS = [
    "filename",
    "path",
    "extension",
    "size_bytes",
    "sha256",
    "status",
    "rule_status",
    "duration",
    "video_codec",
    "width",
    "height",
    "fps",
    "pix_fmt",
    "color_space",
    "color_range",
    "decode_status",
    "total_frames",
    "dropped_frames",
    "decode_errors",
    "average_bit_rate",
    "peak_bit_rate",
    "is_vfr",
    "keyframe_interval_max",
    "output_match",
    "canvas_match",
    "codec_risk_level",
    "realtime_score",
    "manifest_status",
    "integrity_status",
    "warnings",
    "failures",
    "error",
]


def build_report(
    project_path: Path,
    files: list[MediaFileResult],
    rules_path: Path | None = None,
    project_name: str | None = None,
    profile_name: str | None = None,
    live_event: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the top-level report dictionary."""

    summary = build_summary(files)
    report = {
        "project_path": str(Path(project_path).resolve()),
        "total_files": len(files),
        "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        "summary": summary,
        "files": [item.to_dict() for item in files],
    }
    if rules_path is not None:
        report["rules_path"] = str(Path(rules_path).resolve())
    if project_name:
        report["project_name"] = project_name
    if profile_name:
        report["profile_name"] = profile_name
    if live_event:
        report["live_event"] = live_event
    return report


def write_json_report(report: dict[str, Any], output_dir: Path) -> Path:
    """Write media_qc_report.json."""

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "media_qc_report.json"
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def write_csv_report(files: list[MediaFileResult], output_dir: Path) -> Path:
    """Write media_qc_report.csv."""

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "media_qc_report.csv"
    with output_path.open("w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for item in files:
            writer.writerow(_result_to_csv_row(item))
    return output_path


def write_html_report(report: dict[str, Any], output_dir: Path) -> Path:
    """Write media_qc_report.html."""

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "media_qc_report.html"
    env = Environment(
        loader=PackageLoader("mediaqc", "templates"),
        autoescape=select_autoescape(("html", "xml", "j2")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.html.j2")
    output_path.write_text(template.render(report=report), encoding="utf-8")
    return output_path


def build_summary(files: list[MediaFileResult]) -> dict[str, int]:
    """Build pass/warn/fail counts for terminal and HTML reporting."""

    validation_results = [
        result
        for item in files
        for result in item.validation_results
    ]
    decode_reports = [
        item.decode_report
        for item in files
        if item.decode_report is not None
    ]
    return {
        "total": len(files),
        "status_pass": sum(1 for item in files if item.status == "PASS"),
        "status_fail": sum(1 for item in files if item.status == "FAIL"),
        "rule_pass": sum(1 for item in files if item.rule_status == "PASS"),
        "rule_warn": sum(1 for item in files if item.rule_status == "WARN"),
        "rule_fail": sum(1 for item in files if item.rule_status == "FAIL"),
        "validation_pass": sum(1 for result in validation_results if result.status == "PASS"),
        "validation_warn": sum(1 for result in validation_results if result.status == "WARN"),
        "validation_fail": sum(1 for result in validation_results if result.status == "FAIL"),
        "decode_pass": sum(1 for report in decode_reports if report.status == "PASS"),
        "decode_warn": sum(1 for report in decode_reports if report.status == "WARN"),
        "decode_fail": sum(1 for report in decode_reports if report.status == "FAIL"),
    }


def _result_to_csv_row(item: MediaFileResult) -> dict[str, Any]:
    ffprobe = item.ffprobe or {}
    video_stream = _first_stream(ffprobe, "video")
    decode_report = (
        item.decode_report.to_dict()
        if hasattr(item.decode_report, "to_dict")
        else item.decode_report
        or {}
    )

    return {
        "filename": item.filename,
        "path": str(item.path),
        "extension": item.extension,
        "size_bytes": item.size_bytes,
        "sha256": item.sha256 or "",
        "status": item.status,
        "rule_status": item.rule_status,
        "duration": ffprobe.get("duration", ""),
        "video_codec": video_stream.get("codec_name", ""),
        "width": video_stream.get("width", ""),
        "height": video_stream.get("height", ""),
        "fps": video_stream.get("avg_frame_rate", ""),
        "pix_fmt": video_stream.get("pix_fmt", ""),
        "color_space": video_stream.get("color_space", ""),
        "color_range": video_stream.get("color_range", ""),
        "decode_status": decode_report.get("status", ""),
        "total_frames": decode_report.get("total_frames", ""),
        "dropped_frames": decode_report.get("dropped_frames", ""),
        "decode_errors": decode_report.get("decode_errors", ""),
        "average_bit_rate": decode_report.get("average_bit_rate", ""),
        "peak_bit_rate": decode_report.get("peak_bit_rate", ""),
        "is_vfr": decode_report.get("is_vfr", ""),
        "keyframe_interval_max": decode_report.get("keyframe_interval_max", ""),
        "output_match": _status(item.output_match),
        "canvas_match": _status(item.canvas_match),
        "codec_risk_level": getattr(item.codec_profile, "risk_level", "") if item.codec_profile else "",
        "realtime_score": getattr(item.codec_profile, "realtime_score", "") if item.codec_profile else "",
        "manifest_status": item.manifest_status or "",
        "integrity_status": item.integrity_status or "",
        "warnings": "; ".join(item.warnings),
        "failures": "; ".join(item.failures),
        "error": "; ".join(item.errors),
    }


def _first_stream(ffprobe: dict[str, Any], codec_type: str) -> dict[str, Any]:
    for stream in ffprobe.get("streams", []):
        if stream.get("codec_type") == codec_type:
            return stream
    return {}


def _status(value: Any) -> str:
    return getattr(value, "status", "") if value is not None else ""

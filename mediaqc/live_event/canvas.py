"""Multi-screen canvas validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

COMMON_CANVASES = {
    (6400, 2000),
    (7200, 2560),
    (7680, 2160),
    (7680, 4320),
    (15360, 2160),
}


@dataclass(slots=True)
class CanvasReport:
    status: str = "PASS"
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "warnings": self.warnings,
            "failures": self.failures,
            "details": self.details,
        }


def load_canvas_spec(path: Path) -> dict[str, Any]:
    spec_path = Path(path).expanduser()
    raw = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict) or not isinstance(raw.get("canvas"), dict):
        raise ValueError("Canvas spec requires a top-level 'canvas' mapping.")
    return raw


def validate_canvas_spec(spec: dict[str, Any]) -> CanvasReport:
    canvas = spec.get("canvas") or {}
    width = int(canvas.get("width") or 0)
    height = int(canvas.get("height") or 0)
    layout = canvas.get("layout") or []
    report = CanvasReport(details={"canvas": canvas, "coverage_percent": 0})
    if (width, height) not in COMMON_CANVASES:
        report.warnings.append(f"Canvas {width}x{height} is not in the common live-event canvas list.")
    for region in layout:
        x = int(region.get("x") or 0)
        y = int(region.get("y") or 0)
        region_width = int(region.get("width") or 0)
        region_height = int(region.get("height") or 0)
        if x < 0 or y < 0 or x + region_width > width or y + region_height > height:
            report.failures.append(f"Layout region '{region.get('name')}' exceeds canvas bounds.")
    for left_index, left in enumerate(layout):
        for right in layout[left_index + 1 :]:
            if _overlaps(left, right):
                report.failures.append(f"Layout regions '{left.get('name')}' and '{right.get('name')}' overlap.")

    covered = _covered_area(width, height, layout)
    total = width * height if width and height else 0
    coverage = covered / total if total else 0
    report.details["coverage_percent"] = round(coverage * 100, 2)
    if coverage < 0.999:
        report.warnings.append(f"Layout covers {coverage * 100:.2f}% of canvas; expected 100%.")
    if coverage > 1.001:
        report.failures.append("Layout coverage exceeds 100%; overlap or invalid regions detected.")
    return _finalize(report)


def check_media_canvas(media: Any, spec: dict[str, Any]) -> CanvasReport:
    canvas = spec.get("canvas") or {}
    video = _video_stream(media)
    report = CanvasReport(details={"canvas": canvas})
    if not video:
        report.warnings.append("No video stream found for canvas comparison.")
        return _finalize(report)
    width = video.get("width")
    height = video.get("height")
    report.details.update({"media_width": width, "media_height": height})
    if width != canvas.get("width") or height != canvas.get("height"):
        report.warnings.append(
            f"Media resolution {width}x{height} does not match canvas {canvas.get('width')}x{canvas.get('height')}."
        )
    return _finalize(report)


def summarize_canvas(spec: dict[str, Any] | None, layout_report: CanvasReport | None, media_reports: list[CanvasReport]) -> dict[str, Any] | None:
    if spec is None:
        return None
    return {
        "spec": spec,
        "layout": layout_report.to_dict() if layout_report else None,
        "pass": sum(1 for item in media_reports if item.status == "PASS"),
        "warn": sum(1 for item in media_reports if item.status == "WARN"),
        "fail": sum(1 for item in media_reports if item.status == "FAIL"),
    }


def _overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    lx, ly = int(left.get("x") or 0), int(left.get("y") or 0)
    lw, lh = int(left.get("width") or 0), int(left.get("height") or 0)
    rx, ry = int(right.get("x") or 0), int(right.get("y") or 0)
    rw, rh = int(right.get("width") or 0), int(right.get("height") or 0)
    return lx < rx + rw and lx + lw > rx and ly < ry + rh and ly + lh > ry


def _covered_area(width: int, height: int, layout: list[dict[str, Any]]) -> int:
    if not layout:
        return 0
    xs = sorted({0, width} | {int(region.get("x") or 0) for region in layout} | {int(region.get("x") or 0) + int(region.get("width") or 0) for region in layout})
    ys = sorted({0, height} | {int(region.get("y") or 0) for region in layout} | {int(region.get("y") or 0) + int(region.get("height") or 0) for region in layout})
    covered = 0
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            if x2 <= x1 or y2 <= y1:
                continue
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            if any(_contains(region, mid_x, mid_y) for region in layout):
                covered += (x2 - x1) * (y2 - y1)
    return covered


def _contains(region: dict[str, Any], x: float, y: float) -> bool:
    rx, ry = int(region.get("x") or 0), int(region.get("y") or 0)
    rw, rh = int(region.get("width") or 0), int(region.get("height") or 0)
    return rx <= x < rx + rw and ry <= y < ry + rh


def _video_stream(media: Any) -> dict[str, Any]:
    for stream in (getattr(media, "ffprobe", None) or {}).get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return {}


def _finalize(report: CanvasReport) -> CanvasReport:
    if report.failures:
        report.status = "FAIL"
    elif report.warnings:
        report.status = "WARN"
    else:
        report.status = "PASS"
    return report

"""FFmpeg deep media analysis."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from typing import Any

VIDEO_EXTENSIONS = {".mov", ".mp4", ".mxf", ".mkv", ".avi"}
ERROR_PATTERNS = {
    "corrupt_frames": ("corrupt", "corrupted"),
    "missing_frames": ("missing", "concealing"),
    "decode_errors": ("decode", "error while decoding", "invalid data"),
    "timestamp_errors": ("timestamp", "non monoton", "dts", "pts"),
    "packet_errors": ("packet", "invalid nal", "truncated"),
}


class FFmpegNotFoundError(RuntimeError):
    """Raised when ffmpeg is unavailable."""


@dataclass(slots=True)
class DecodeReport:
    status: str = "PASS"
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    ffmpeg_returncode: int | None = None
    total_frames: int = 0
    dropped_frames: int = 0
    decode_errors: int = 0
    corrupt_frames: int = 0
    missing_frames: int = 0
    timestamp_errors: int = 0
    packet_errors: int = 0
    average_bit_rate: int | None = None
    peak_bit_rate: int | None = None
    is_vfr: bool = False
    keyframe_interval_max: float | None = None
    keyframe_interval_avg: float | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "warnings": self.warnings,
            "failures": self.failures,
            "ffmpeg_returncode": self.ffmpeg_returncode,
            "total_frames": self.total_frames,
            "dropped_frames": self.dropped_frames,
            "decode_errors": self.decode_errors,
            "corrupt_frames": self.corrupt_frames,
            "missing_frames": self.missing_frames,
            "timestamp_errors": self.timestamp_errors,
            "packet_errors": self.packet_errors,
            "average_bit_rate": self.average_bit_rate,
            "peak_bit_rate": self.peak_bit_rate,
            "is_vfr": self.is_vfr,
            "keyframe_interval_max": self.keyframe_interval_max,
            "keyframe_interval_avg": self.keyframe_interval_avg,
            "details": self.details,
        }


def analyze_media(path: Path, ffprobe: dict[str, Any] | None = None) -> DecodeReport:
    """Run deep FFmpeg analysis for supported video containers."""

    media_path = Path(path)
    report = DecodeReport()
    if media_path.suffix.lower() not in VIDEO_EXTENSIONS:
        report.status = "PASS"
        report.details["skipped"] = "Deep analysis is only enabled for video containers."
        return report

    ffmpeg = ensure_ffmpeg_available()
    decode_result = _run_decode_check(ffmpeg, media_path)
    report.ffmpeg_returncode = decode_result.returncode
    stderr = decode_result.stderr or ""
    _apply_error_counts(report, stderr)

    if decode_result.returncode != 0:
        report.failures.append(f"ffmpeg decode check failed with exit code {decode_result.returncode}.")
    if stderr.strip():
        report.details["ffmpeg_error_log"] = _trim_log(stderr)

    try:
        frame_packet_data = _probe_frames_and_packets(media_path)
        _apply_frame_stats(report, frame_packet_data)
        _apply_packet_stats(report, frame_packet_data, ffprobe)
    except Exception as exc:  # noqa: BLE001 - deep analysis should report and continue.
        report.warnings.append(f"Unable to collect frame/packet metrics: {exc}")

    _finalize_status(report)
    return report


def ensure_ffmpeg_available() -> str:
    from .processing.ffmpeg_runner import FFmpegNotFoundError as ProcessingFFmpegNotFoundError
    from .processing.ffmpeg_runner import check_ffmpeg_available

    try:
        return check_ffmpeg_available()
    except ProcessingFFmpegNotFoundError as exc:
        raise FFmpegNotFoundError(
            "ffmpeg was not found. Install FFmpeg and make sure ffmpeg is on PATH."
        ) from exc


def _run_decode_check(ffmpeg: str, path: Path) -> subprocess.CompletedProcess[str]:
    command = [
        ffmpeg,
        "-v",
        "error",
        "-i",
        str(path),
        "-f",
        "null",
        "-",
    ]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )


def _probe_frames_and_packets(path: Path) -> dict[str, Any]:
    from .processing.ffmpeg_runner import FFprobeNotFoundError, check_ffprobe_available

    try:
        ffprobe = check_ffprobe_available()
    except FFprobeNotFoundError as exc:
        raise RuntimeError("ffprobe was not found while collecting deep metrics.") from exc

    command = [
        ffprobe,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-select_streams",
        "v:0",
        "-show_entries",
        "frame=best_effort_timestamp_time,pkt_pts_time,pkt_dts_time,pkt_duration_time,key_frame:"
        "packet=pts_time,dts_time,duration_time,size,flags",
        "-show_frames",
        "-show_packets",
        str(path),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"ffprobe deep metrics failed with exit code {completed.returncode}.")
    return json.loads(completed.stdout or "{}")


def _apply_error_counts(report: DecodeReport, stderr: str) -> None:
    counts = count_error_patterns(stderr)
    report.corrupt_frames = counts["corrupt_frames"]
    report.missing_frames = counts["missing_frames"]
    report.decode_errors = counts["decode_errors"]
    report.timestamp_errors = counts["timestamp_errors"]
    report.packet_errors = counts["packet_errors"]

    if report.corrupt_frames:
        report.failures.append(f"Corrupt frame messages: {report.corrupt_frames}.")
    if report.decode_errors:
        report.failures.append(f"Decode errors: {report.decode_errors}.")
    if report.packet_errors:
        report.failures.append(f"Packet errors: {report.packet_errors}.")
    if report.missing_frames:
        report.warnings.append(f"Missing frame messages: {report.missing_frames}.")
    if report.timestamp_errors:
        report.warnings.append(f"Timestamp errors: {report.timestamp_errors}.")


def _apply_frame_stats(report: DecodeReport, data: dict[str, Any]) -> None:
    frames = data.get("frames") or []
    timestamps = [_frame_timestamp(frame) for frame in frames]
    timestamps = [value for value in timestamps if value is not None]
    report.total_frames = len(frames)
    report.is_vfr = detect_vfr(timestamps)
    report.dropped_frames = estimate_dropped_frames(timestamps)
    report.keyframe_interval_max, report.keyframe_interval_avg = calculate_keyframe_intervals(frames)

    if report.dropped_frames:
        report.warnings.append(f"Possible dropped/missing frames: {report.dropped_frames}.")
    if report.is_vfr:
        report.warnings.append("Variable frame rate detected.")


def _apply_packet_stats(
    report: DecodeReport,
    data: dict[str, Any],
    ffprobe: dict[str, Any] | None,
) -> None:
    packets = data.get("packets") or []
    report.average_bit_rate = _parse_int((ffprobe or {}).get("bit_rate"))
    report.peak_bit_rate = calculate_peak_bit_rate(packets)


def count_error_patterns(stderr: str) -> dict[str, int]:
    lines = stderr.splitlines()
    counts: dict[str, int] = {}
    for key, patterns in ERROR_PATTERNS.items():
        counts[key] = sum(
            1
            for line in lines
            if any(pattern in line.casefold() for pattern in patterns)
        )
    return counts


def detect_vfr(timestamps: list[float], tolerance: float = 0.002) -> bool:
    if len(timestamps) < 4:
        return False
    deltas = _positive_deltas(timestamps)
    if len(deltas) < 3:
        return False
    expected = median(deltas)
    return any(abs(delta - expected) > tolerance for delta in deltas)


def estimate_dropped_frames(timestamps: list[float]) -> int:
    deltas = _positive_deltas(timestamps)
    if len(deltas) < 3:
        return 0
    expected = median(deltas)
    if expected <= 0:
        return 0
    dropped = 0
    for delta in deltas:
        if delta > expected * 1.5:
            dropped += max(1, round(delta / expected) - 1)
    return dropped


def calculate_keyframe_intervals(frames: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    keyframe_times = [
        timestamp
        for frame in frames
        if str(frame.get("key_frame")) == "1"
        for timestamp in [_frame_timestamp(frame)]
        if timestamp is not None
    ]
    intervals = _positive_deltas(keyframe_times)
    if not intervals:
        return None, None
    return max(intervals), sum(intervals) / len(intervals)


def calculate_peak_bit_rate(packets: list[dict[str, Any]]) -> int | None:
    buckets: dict[int, int] = {}
    for packet in packets:
        timestamp = _parse_float(packet.get("pts_time") or packet.get("dts_time"))
        size = _parse_int(packet.get("size"))
        if timestamp is None or size is None:
            continue
        bucket = int(timestamp)
        buckets[bucket] = buckets.get(bucket, 0) + size
    if not buckets:
        return None
    return max(value * 8 for value in buckets.values())


def _finalize_status(report: DecodeReport) -> None:
    if report.failures:
        report.status = "FAIL"
    elif report.warnings:
        report.status = "WARN"
    else:
        report.status = "PASS"


def _frame_timestamp(frame: dict[str, Any]) -> float | None:
    return _parse_float(
        frame.get("best_effort_timestamp_time")
        or frame.get("pkt_pts_time")
        or frame.get("pkt_dts_time")
    )


def _positive_deltas(values: list[float]) -> list[float]:
    sorted_values = sorted(values)
    return [
        round(current - previous, 6)
        for previous, current in zip(sorted_values, sorted_values[1:])
        if current > previous
    ]


def _parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _trim_log(stderr: str, max_lines: int = 50) -> list[str]:
    lines = [line for line in stderr.splitlines() if line.strip()]
    return lines[:max_lines]

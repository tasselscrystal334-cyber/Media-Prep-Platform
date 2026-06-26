from mediaqc.deep_analysis import (
    DecodeReport,
    calculate_keyframe_intervals,
    calculate_peak_bit_rate,
    count_error_patterns,
    detect_vfr,
    estimate_dropped_frames,
)


def test_count_error_patterns() -> None:
    stderr = """
[mov] Packet corrupt
error while decoding MB 1 2
Non-monotonous DTS in output stream
concealing 10 DC, 10 AC, 10 MV errors in P frame
"""

    counts = count_error_patterns(stderr)

    assert counts["corrupt_frames"] == 1
    assert counts["decode_errors"] >= 1
    assert counts["timestamp_errors"] == 1
    assert counts["missing_frames"] == 1
    assert counts["packet_errors"] == 1


def test_detect_vfr_and_dropped_frames() -> None:
    timestamps = [0.0, 1 / 30, 2 / 30, 4 / 30, 5 / 30]

    assert detect_vfr(timestamps) is True
    assert estimate_dropped_frames(timestamps) == 1


def test_calculate_peak_bit_rate() -> None:
    packets = [
        {"pts_time": "0.10", "size": "100"},
        {"pts_time": "0.90", "size": "200"},
        {"pts_time": "1.10", "size": "50"},
    ]

    assert calculate_peak_bit_rate(packets) == 2400


def test_calculate_keyframe_intervals() -> None:
    frames = [
        {"best_effort_timestamp_time": "0.0", "key_frame": 1},
        {"best_effort_timestamp_time": "1.0", "key_frame": 0},
        {"best_effort_timestamp_time": "2.0", "key_frame": 1},
        {"best_effort_timestamp_time": "5.0", "key_frame": 1},
    ]

    max_interval, avg_interval = calculate_keyframe_intervals(frames)

    assert max_interval == 3.0
    assert avg_interval == 2.5


def test_decode_report_to_dict() -> None:
    report = DecodeReport(status="WARN", total_frames=10, dropped_frames=1)
    report.warnings.append("Variable frame rate detected.")

    data = report.to_dict()

    assert data["status"] == "WARN"
    assert data["total_frames"] == 10
    assert data["dropped_frames"] == 1
    assert data["warnings"] == ["Variable frame rate detected."]

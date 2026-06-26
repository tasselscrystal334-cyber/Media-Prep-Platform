from pathlib import Path

from mediaqc.models import MediaFileResult
from mediaqc.deep_analysis import DecodeReport
from mediaqc.report import build_report, write_html_report


def test_write_html_report(tmp_path: Path) -> None:
    item = MediaFileResult(
        path=tmp_path / "Opening.mov",
        filename="Opening.mov",
        extension=".mov",
        size_bytes=123,
        sha256="abc123",
        ffprobe={
            "format_name": "mov,mp4",
            "duration": "60.000000",
            "bit_rate": "800000000",
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "hap",
                    "width": 3840,
                    "height": 2160,
                    "avg_frame_rate": "60/1",
                    "pix_fmt": "rgb0",
                    "color_space": "bt709",
                    "color_range": "pc",
                }
            ],
        },
    )
    item.rule_status = "WARN"
    item.warnings.append("File size is below minimum.")
    item.decode_report = DecodeReport(status="WARN", total_frames=100, dropped_frames=1)
    item.decode_report.warnings.append("Variable frame rate detected.")
    report = build_report(tmp_path, [item], project_name="LED Show 2026")

    output_path = write_html_report(report, tmp_path)

    assert output_path.name == "media_qc_report.html"
    html = output_path.read_text(encoding="utf-8")
    assert "LED Show 2026" in html
    assert "Opening.mov" in html
    assert "WARN" in html
    assert "Total Frames" in html
    assert "Variable frame rate detected." in html
    assert "File size is below minimum." in html

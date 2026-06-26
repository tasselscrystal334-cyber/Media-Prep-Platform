from pathlib import Path

from mediaqc.report import write_pdf_report


def test_write_pdf_report_creates_pdf(tmp_path: Path) -> None:
    report = {
        "project_path": str(tmp_path),
        "generated_at": "2026-06-27T12:00:00",
        "total_files": 1,
        "summary": {"rule_pass": 1, "rule_warn": 0, "rule_fail": 0},
        "files": [
            {
                "filename": "Opening.mov",
                "extension": ".mov",
                "size_bytes": 123,
                "status": "PASS",
                "rule_status": "PASS",
                "errors": [],
            }
        ],
    }

    pdf_path = write_pdf_report(report, tmp_path)

    assert pdf_path.name == "media_qc_report.pdf"
    assert pdf_path.read_bytes().startswith(b"%PDF-1.4")

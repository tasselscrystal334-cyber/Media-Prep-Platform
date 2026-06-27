"""Background scan worker for the PySide6 GUI."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any


class ScanWorker:
    """Non-Qt worker logic used by the Qt thread wrapper and tests."""

    def __init__(self, project_path: Path, output_path: Path, html: bool = True, pdf: bool = True) -> None:
        self.project_path = Path(project_path)
        self.output_path = Path(output_path)
        self.html = html
        self.pdf = pdf
        self.cancel_event = threading.Event()

    def cancel(self) -> None:
        self.cancel_event.set()

    def run(self) -> dict[str, Any]:
        if self.cancel_event.is_set():
            return {"status": "CANCELLED", "message": "Scan cancelled before start."}
        from mediaqc.cli import _run_scan

        files, json_path, csv_path, html_path, db_path = _run_scan(
            project_path=self.project_path,
            output=self.output_path,
            database=self.output_path / "media.db",
            project_rules=None,
            active_rules_path=None,
            html=self.html,
            deep=False,
            output_spec_path=None,
            canvas_spec_path=None,
            write_manifest_files=False,
            show_progress=False,
        )
        pdf_path = None
        if self.pdf:
            from mediaqc.report import build_report, write_pdf_report

            report = build_report(self.project_path, files)
            pdf_path = write_pdf_report(report, self.output_path)
        status = "CANCELLED" if self.cancel_event.is_set() else "SUCCESS"
        return {
            "status": status,
            "files": len(files),
            "json_path": json_path,
            "csv_path": csv_path,
            "html_path": html_path,
            "pdf_path": pdf_path,
            "db_path": db_path,
        }

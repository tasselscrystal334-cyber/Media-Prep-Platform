import json
from pathlib import Path

from mediaqc.diagnostics import build_install_report, write_exception_log
from mediaqc.updater import compare_versions, normalize_version


def test_install_report_writes_log_path(tmp_path: Path) -> None:
    report = build_install_report(tmp_path)

    assert report.status in {"PASS", "WARN", "FAIL"}
    assert report.log_path is not None
    assert Path(report.log_path).exists()
    assert any(check.name == "python" for check in report.checks)


def test_exception_log_contains_context(tmp_path: Path) -> None:
    try:
        raise ValueError("bad media path")
    except ValueError as exc:
        path = write_exception_log(exc, tmp_path, {"command": "scan"})

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["exception_type"] == "ValueError"
    assert payload["context"]["command"] == "scan"
    assert payload["traceback"]


def test_version_helpers() -> None:
    assert normalize_version("v2.0.1") == "2.0.1"
    assert compare_versions("2.1.0", "2.0.9") == 1
    assert compare_versions("2.0.0", "2.0") == 0
    assert compare_versions("1.9.9", "2.0.0") == -1

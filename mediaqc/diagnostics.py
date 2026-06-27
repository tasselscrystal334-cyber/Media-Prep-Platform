"""Installation checks and local diagnostics for MediaQC."""

from __future__ import annotations

import json
import logging
import os
import platform
import sys
import traceback
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .processing.ffmpeg_runner import build_doctor_report


LOGGER_NAME = "mediaqc"


def utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def default_log_dir() -> Path:
    configured = os.getenv("MEDIAQC_LOG_DIR")
    if configured:
        return Path(configured).expanduser()
    if sys.platform.startswith("win"):
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "MediaQC" / "logs"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Logs" / "MediaQC"
    return Path(os.getenv("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "mediaqc" / "logs"


def configure_logging(log_dir: Path | None = None, debug: bool = False) -> Path:
    directory = Path(log_dir) if log_dir else default_log_dir()
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / "mediaqc.log"
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    if not any(isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_path for handler in logger.handlers):
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.info("MediaQC logging initialized")
    return log_path


def write_exception_log(exc: BaseException, log_dir: Path | None = None, context: dict[str, Any] | None = None) -> Path:
    directory = Path(log_dir) if log_dir else default_log_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"error-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.log"
    payload = {
        "generated_at": utc_timestamp(),
        "version": __version__,
        "exception_type": type(exc).__name__,
        "message": str(exc),
        "context": context or {},
        "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.getLogger(LOGGER_NAME).exception("Unhandled error logged to %s", path)
    return path


@dataclass(slots=True)
class InstallCheck:
    name: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "status": self.status, "message": self.message, "details": self.details}


@dataclass(slots=True)
class InstallReport:
    status: str
    generated_at: str
    checks: list[InstallCheck]
    log_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "generated_at": self.generated_at,
            "checks": [check.to_dict() for check in self.checks],
            "log_path": self.log_path,
        }


def build_install_report(log_dir: Path | None = None) -> InstallReport:
    log_path = configure_logging(log_dir)
    checks = [
        check_python_version(),
        check_package_version(),
        check_write_access(log_path.parent),
        check_ffmpeg_tools(),
    ]
    status = "PASS"
    if any(check.status == "FAIL" for check in checks):
        status = "FAIL"
    elif any(check.status == "WARN" for check in checks):
        status = "WARN"
    return InstallReport(status=status, generated_at=utc_timestamp(), checks=checks, log_path=str(log_path))


def check_python_version() -> InstallCheck:
    current = sys.version_info
    status = "PASS" if current >= (3, 11) else "FAIL"
    return InstallCheck(
        name="python",
        status=status,
        message=f"Python {platform.python_version()}",
        details={"executable": sys.executable, "required": ">=3.11"},
    )


def check_package_version() -> InstallCheck:
    return InstallCheck(name="mediaqc", status="PASS", message=f"MediaQC {__version__}", details={"version": __version__})


def check_write_access(path: Path) -> InstallCheck:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".mediaqc-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        return InstallCheck(name="log_write_access", status="FAIL", message=str(exc), details={"path": str(path)})
    return InstallCheck(name="log_write_access", status="PASS", message="Log directory is writable.", details={"path": str(path)})


def check_ffmpeg_tools() -> InstallCheck:
    doctor = build_doctor_report()
    status = "PASS" if doctor.ffmpeg_path and doctor.ffprobe_path else "FAIL"
    if status == "PASS" and not doctor.ffplay_path:
        status = "WARN"
    message = "FFmpeg tools detected." if status != "FAIL" else "ffmpeg/ffprobe not found."
    return InstallCheck(name="ffmpeg_tools", status=status, message=message, details=doctor.to_dict())

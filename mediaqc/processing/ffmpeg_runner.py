"""Safe FFmpeg, FFprobe, and FFplay command execution."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class FFmpegNotFoundError(RuntimeError):
    """Raised when ffmpeg is unavailable."""


class FFprobeNotFoundError(RuntimeError):
    """Raised when ffprobe is unavailable."""


class FFplayNotFoundError(RuntimeError):
    """Raised when ffplay is unavailable."""


class EncoderNotAvailableError(RuntimeError):
    """Raised when a requested encoder backend is unavailable."""


@dataclass(slots=True)
class CommandResult:
    command: list[str]
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    dry_run: bool = False
    log_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "dry_run": self.dry_run,
            "log_path": str(self.log_path) if self.log_path else None,
        }


@dataclass(slots=True)
class DoctorReport:
    ffmpeg_path: str | None = None
    ffprobe_path: str | None = None
    ffplay_path: str | None = None
    ffmpeg_version: str | None = None
    encoders_count: int = 0
    decoders_count: int = 0
    filters_count: int = 0
    hap_support: bool = False
    prores_support: bool = False
    libx264_support: bool = False
    libx265_support: bool = False
    notchlc_decode_support: bool = False
    notchlc_encode_support: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ffmpeg_path": self.ffmpeg_path,
            "ffprobe_path": self.ffprobe_path,
            "ffplay_path": self.ffplay_path,
            "ffmpeg_version": self.ffmpeg_version,
            "encoders_count": self.encoders_count,
            "decoders_count": self.decoders_count,
            "filters_count": self.filters_count,
            "hap_support": self.hap_support,
            "prores_support": self.prores_support,
            "libx264_support": self.libx264_support,
            "libx265_support": self.libx265_support,
            "notchlc_decode_support": self.notchlc_decode_support,
            "notchlc_encode_support": self.notchlc_encode_support,
            "errors": self.errors,
        }


def check_ffmpeg_available() -> str:
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise FFmpegNotFoundError("ffmpeg was not found. Install FFmpeg and make sure ffmpeg is on PATH.")
    return executable


def check_ffprobe_available() -> str:
    executable = shutil.which("ffprobe")
    if executable is None:
        raise FFprobeNotFoundError("ffprobe was not found. Install FFmpeg and make sure ffprobe is on PATH.")
    return executable


def check_ffplay_available() -> str:
    executable = shutil.which("ffplay")
    if executable is None:
        raise FFplayNotFoundError(
            "ffplay was not found. Install a full FFmpeg package and make sure ffplay is on PATH."
        )
    return executable


def run_ffmpeg(args: list[str], log_path: Path | None = None, dry_run: bool = False) -> CommandResult:
    command = [check_ffmpeg_available(), *[str(arg) for arg in args]]
    return run_command(command, log_path=log_path, dry_run=dry_run)


def run_ffplay(args: list[str], dry_run: bool = False) -> CommandResult:
    command = [check_ffplay_available(), *[str(arg) for arg in args]]
    return run_command(command, dry_run=dry_run)


def run_command(command: list[str], log_path: Path | None = None, dry_run: bool = False) -> CommandResult:
    command = [str(part) for part in command]
    if dry_run:
        result = CommandResult(command=command, dry_run=True, log_path=log_path)
        _write_log(log_path, result)
        return result
    command = _resolve_known_tool(command)
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    result = CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        dry_run=False,
        log_path=log_path,
    )
    _write_log(log_path, result)
    return result


def _resolve_known_tool(command: list[str]) -> list[str]:
    if not command:
        return command
    tool = Path(command[0]).name
    if tool == "ffmpeg":
        command[0] = check_ffmpeg_available()
    elif tool == "ffprobe":
        command[0] = check_ffprobe_available()
    elif tool == "ffplay":
        command[0] = check_ffplay_available()
    return command


def get_available_encoders() -> set[str]:
    return _parse_codec_names(_run_ffmpeg_capability("-encoders"))


def get_available_decoders() -> set[str]:
    return _parse_codec_names(_run_ffmpeg_capability("-decoders"))


def get_available_filters() -> set[str]:
    lines = _run_ffmpeg_capability("-filters").splitlines()
    filters: set[str] = set()
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and not parts[0].startswith("-") and "." in parts[0]:
            filters.add(parts[1])
    return filters


def get_ffmpeg_version() -> str | None:
    try:
        result = run_command([check_ffmpeg_available(), "-version"], dry_run=False)
    except FFmpegNotFoundError:
        return None
    first_line = (result.stdout or result.stderr).splitlines()
    return first_line[0] if first_line else None


def build_doctor_report() -> DoctorReport:
    report = DoctorReport()
    try:
        report.ffmpeg_path = check_ffmpeg_available()
        report.ffmpeg_version = get_ffmpeg_version()
    except FFmpegNotFoundError as exc:
        report.errors.append(str(exc))
    try:
        report.ffprobe_path = check_ffprobe_available()
    except FFprobeNotFoundError as exc:
        report.errors.append(str(exc))
    try:
        report.ffplay_path = check_ffplay_available()
    except FFplayNotFoundError as exc:
        report.errors.append(str(exc))

    if report.ffmpeg_path:
        encoders = get_available_encoders()
        decoders = get_available_decoders()
        filters = get_available_filters()
        report.encoders_count = len(encoders)
        report.decoders_count = len(decoders)
        report.filters_count = len(filters)
        report.hap_support = "hap" in encoders or "hap" in decoders
        report.prores_support = any(name.startswith("prores") for name in encoders | decoders)
        report.libx264_support = "libx264" in encoders
        report.libx265_support = "libx265" in encoders
        report.notchlc_decode_support = "notchlc" in decoders
        report.notchlc_encode_support = "notchlc" in encoders
    return report


def _run_ffmpeg_capability(flag: str) -> str:
    try:
        command = [check_ffmpeg_available(), "-hide_banner", flag]
    except FFmpegNotFoundError:
        return ""
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    return (completed.stdout or "") + "\n" + (completed.stderr or "")


def _parse_codec_names(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and not parts[0].startswith("-") and "." in parts[0]:
            names.add(parts[1])
    return names


def _write_log(log_path: Path | None, result: CommandResult) -> None:
    if log_path is None:
        return
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "COMMAND:",
                " ".join(result.command),
                "",
                f"RETURN CODE: {result.returncode}",
                f"DRY RUN: {result.dry_run}",
                "",
                "STDOUT:",
                result.stdout,
                "",
                "STDERR:",
                result.stderr,
            ]
        ),
        encoding="utf-8",
    )

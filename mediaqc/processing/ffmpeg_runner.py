"""Safe FFmpeg, FFprobe, and FFplay command execution."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .tool_installer import ToolInstallError, default_tool_install_dir, ensure_ffmpeg_bundle_installed


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
    ffmpeg_source: str | None = None
    ffprobe_source: str | None = None
    ffplay_source: str | None = None
    bundled_tools_dir: str | None = None
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
    adobe_media_encoder_path: str | None = None
    notchlc_adobe_plugin_hint: bool = False
    auto_install_dir: str | None = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ffmpeg_path": self.ffmpeg_path,
            "ffprobe_path": self.ffprobe_path,
            "ffplay_path": self.ffplay_path,
            "ffmpeg_source": self.ffmpeg_source,
            "ffprobe_source": self.ffprobe_source,
            "ffplay_source": self.ffplay_source,
            "bundled_tools_dir": self.bundled_tools_dir,
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
            "adobe_media_encoder_path": self.adobe_media_encoder_path,
            "notchlc_adobe_plugin_hint": self.notchlc_adobe_plugin_hint,
            "auto_install_dir": self.auto_install_dir,
            "errors": self.errors,
        }


def check_ffmpeg_available() -> str:
    executable = resolve_tool_path("ffmpeg", auto_install=True)
    if executable.path is None:
        raise FFmpegNotFoundError("ffmpeg was not found. Install FFmpeg and make sure ffmpeg is on PATH.")
    return executable.path


def check_ffprobe_available() -> str:
    executable = resolve_tool_path("ffprobe", auto_install=True)
    if executable.path is None:
        raise FFprobeNotFoundError("ffprobe was not found. Install FFmpeg and make sure ffprobe is on PATH.")
    return executable.path


def check_ffplay_available() -> str:
    executable = resolve_tool_path("ffplay", auto_install=True)
    if executable.path is None:
        raise FFplayNotFoundError(
            "ffplay was not found. Install a full FFmpeg package and make sure ffplay is on PATH."
        )
    return executable.path


@dataclass(slots=True)
class ToolResolution:
    name: str
    path: str | None
    source: str


def resolve_tool_path(name: str, auto_install: bool = False) -> ToolResolution:
    """Resolve ffmpeg-family tools from env, bundled folders, then PATH."""

    resolved = _resolve_tool_path_without_install(name)
    if resolved.path or not auto_install:
        return resolved
    try:
        result = ensure_ffmpeg_bundle_installed()
    except ToolInstallError:
        return resolved
    candidate = _tool_candidate(result.install_dir, name)
    if _is_executable_file(candidate):
        return ToolResolution(name=name, path=str(candidate), source="auto-installed tools")
    return resolved


def _resolve_tool_path_without_install(name: str) -> ToolResolution:
    env_key = f"MEDIAQC_{name.upper()}_PATH"
    explicit_path = os.getenv(env_key)
    if explicit_path:
        path = Path(explicit_path).expanduser()
        if _is_executable_file(path):
            return ToolResolution(name=name, path=str(path), source=env_key)

    for directory, source in _candidate_tool_dirs():
        candidate = _tool_candidate(directory, name)
        if _is_executable_file(candidate):
            return ToolResolution(name=name, path=str(candidate), source=source)

    path_from_env = shutil.which(name)
    if path_from_env:
        return ToolResolution(name=name, path=path_from_env, source="PATH")
    return ToolResolution(name=name, path=None, source="not_found")


def get_bundled_tools_dir() -> Path | None:
    for directory, _source in _candidate_tool_dirs():
        if any(_is_executable_file(_tool_candidate(directory, name)) for name in ("ffmpeg", "ffprobe", "ffplay")):
            return directory
    return None


def _candidate_tool_dirs() -> list[tuple[Path, str]]:
    dirs: list[tuple[Path, str]] = []
    env_dir = os.getenv("MEDIAQC_FFMPEG_DIR")
    if env_dir:
        dirs.append((Path(env_dir).expanduser(), "MEDIAQC_FFMPEG_DIR"))
    dirs.append((default_tool_install_dir(), "auto install cache"))

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = Path(str(meipass))
        dirs.extend(
            [
                (base / "tools" / "plugins" / "ffmpeg", "PyInstaller bundle plugins"),
                (base / "tools", "PyInstaller bundle"),
                (base / "ffmpeg", "PyInstaller bundle"),
            ]
        )

    executable_dir = Path(sys.executable).resolve().parent
    dirs.extend(
        [
            (executable_dir / "tools" / "plugins" / "ffmpeg", "bundled plugin tools"),
            (executable_dir / "tools", "bundled tools"),
            (executable_dir.parent / "tools" / "plugins" / "ffmpeg", "bundled plugin tools"),
            (executable_dir.parent / "tools", "bundled tools"),
            (Path.cwd() / "tools" / "plugins" / "ffmpeg", "working directory plugin tools"),
            (Path.cwd() / "tools", "working directory tools"),
        ]
    )
    return dirs


def _tool_candidate(directory: Path, name: str) -> Path:
    exe_name = f"{name}.exe" if sys.platform.startswith("win") else name
    return directory / exe_name


def _is_executable_file(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


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
    from .adobe_ame import detect_adobe_media_encoder, detect_notchlc_adobe_plugin_hint

    report = DoctorReport()
    report.auto_install_dir = str(default_tool_install_dir())
    try:
        ffmpeg = resolve_tool_path("ffmpeg", auto_install=True)
        report.ffmpeg_path = ffmpeg.path
        report.ffmpeg_source = ffmpeg.source
        if ffmpeg.path is None:
            raise FFmpegNotFoundError("ffmpeg was not found. Install FFmpeg and make sure ffmpeg is on PATH.")
        report.ffmpeg_version = get_ffmpeg_version()
    except FFmpegNotFoundError as exc:
        report.errors.append(str(exc))
    try:
        ffprobe = resolve_tool_path("ffprobe", auto_install=True)
        report.ffprobe_path = ffprobe.path
        report.ffprobe_source = ffprobe.source
        if ffprobe.path is None:
            raise FFprobeNotFoundError("ffprobe was not found. Install FFmpeg and make sure ffprobe is on PATH.")
    except FFprobeNotFoundError as exc:
        report.errors.append(str(exc))
    try:
        ffplay = resolve_tool_path("ffplay", auto_install=True)
        report.ffplay_path = ffplay.path
        report.ffplay_source = ffplay.source
        if ffplay.path is None:
            raise FFplayNotFoundError("ffplay was not found. Install a full FFmpeg package and make sure ffplay is on PATH.")
    except FFplayNotFoundError as exc:
        report.errors.append(str(exc))
    bundled_tools = get_bundled_tools_dir()
    report.bundled_tools_dir = str(bundled_tools) if bundled_tools else None

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
    ame_path = detect_adobe_media_encoder()
    report.adobe_media_encoder_path = str(ame_path) if ame_path else None
    report.notchlc_adobe_plugin_hint = detect_notchlc_adobe_plugin_hint()
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

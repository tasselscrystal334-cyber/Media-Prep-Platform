"""Download and install FFmpeg-family tools for Loom."""

from __future__ import annotations

import os
import platform
import shutil
import stat
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


TOOL_NAMES = ("ffmpeg", "ffprobe", "ffplay")


class ToolInstallError(RuntimeError):
    """Raised when Loom cannot install FFmpeg tools automatically."""


@dataclass(slots=True)
class ToolInstallResult:
    install_dir: Path
    downloaded: bool
    source_url: str


def auto_download_enabled() -> bool:
    value = os.getenv("LOOM_DISABLE_TOOL_DOWNLOAD") or os.getenv("MEDIAQC_DISABLE_TOOL_DOWNLOAD")
    return str(value or "").strip().casefold() not in {"1", "true", "yes", "on"}


def default_tool_install_dir() -> Path:
    configured = os.getenv("LOOM_TOOLS_DIR") or os.getenv("MEDIAQC_FFMPEG_DIR")
    if configured:
        return Path(configured).expanduser()
    return application_tools_plugins_dir() / "ffmpeg"


def application_tools_plugins_dir() -> Path:
    """Return the software-local tools/plugins directory."""

    return _application_root() / "tools" / "plugins"


def ensure_ffmpeg_bundle_installed() -> ToolInstallResult:
    install_dir = default_tool_install_dir()
    if all(_is_executable_file(_tool_candidate(install_dir, name)) for name in TOOL_NAMES):
        return ToolInstallResult(install_dir=install_dir, downloaded=False, source_url="")

    if not auto_download_enabled():
        raise ToolInstallError("automatic FFmpeg tool download is disabled")

    url = _package_url()
    install_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="loom-ffmpeg-") as tmp:
        archive_path = Path(tmp) / Path(url).name
        _download(url, archive_path)
        extract_dir = Path(tmp) / "extract"
        extract_dir.mkdir()
        _extract_archive(archive_path, extract_dir)
        _install_tools(extract_dir, install_dir)
    return ToolInstallResult(install_dir=install_dir, downloaded=True, source_url=url)


def _package_url() -> str:
    configured = os.getenv("LOOM_FFMPEG_PACKAGE_URL") or os.getenv("MEDIAQC_FFMPEG_PACKAGE_URL")
    if configured:
        return configured
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Darwin":
        arch = "macosarm64" if machine in {"arm64", "aarch64"} else "macos64"
        return f"https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-{arch}-gpl.zip"
    if system == "Windows":
        return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    if system == "Linux":
        arch = "linuxarm64" if machine in {"arm64", "aarch64"} else "linux64"
        return f"https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-{arch}-gpl.tar.xz"
    raise ToolInstallError(f"automatic FFmpeg download is not supported on {system}")


def _application_root() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(str(meipass)).resolve()
    source_root = Path(__file__).resolve().parents[2]
    if (source_root / "pyproject.toml").exists():
        return source_root
    return Path(sys.executable).resolve().parent


def _download(url: str, destination: Path) -> None:
    try:
        urllib.request.urlretrieve(url, destination)
    except Exception as exc:  # noqa: BLE001 - convert network errors to clear install errors.
        raise ToolInstallError(f"failed to download FFmpeg tools from {url}: {exc}") from exc


def _extract_archive(archive_path: Path, destination: Path) -> None:
    suffixes = "".join(archive_path.suffixes)
    try:
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(destination)
            return
        if suffixes.endswith(".tar.xz") or suffixes.endswith(".tar.gz") or archive_path.suffix == ".tar":
            with tarfile.open(archive_path) as archive:
                archive.extractall(destination, filter="data")
            return
    except Exception as exc:  # noqa: BLE001
        raise ToolInstallError(f"failed to extract FFmpeg archive {archive_path}: {exc}") from exc
    raise ToolInstallError(f"unsupported FFmpeg archive type: {archive_path.name}")


def _install_tools(source_root: Path, install_dir: Path) -> None:
    missing: list[str] = []
    for name in TOOL_NAMES:
        source = _find_extracted_tool(source_root, name)
        if source is None:
            missing.append(name)
            continue
        target = _tool_candidate(install_dir, name)
        shutil.copy2(source, target)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if missing:
        raise ToolInstallError(f"downloaded FFmpeg package did not contain: {', '.join(missing)}")


def _find_extracted_tool(source_root: Path, name: str) -> Path | None:
    candidates = [path for path in source_root.rglob(_tool_filename(name)) if path.is_file()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: len(path.parts))[0]


def _tool_candidate(directory: Path, name: str) -> Path:
    return directory / _tool_filename(name)


def _tool_filename(name: str) -> str:
    return f"{name}.exe" if platform.system() == "Windows" else name


def _is_executable_file(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)

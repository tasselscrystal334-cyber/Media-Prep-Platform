"""Optional MediaInfo integration."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


class MediaInfoNotFoundError(RuntimeError):
    """Raised when MediaInfo CLI is unavailable."""


def check_mediainfo_available() -> str:
    executable = shutil.which("mediainfo")
    if executable is None:
        raise MediaInfoNotFoundError("mediainfo was not found. Install MediaInfo CLI to enable MediaInfo metadata.")
    return executable


def probe_mediainfo(path: Path) -> dict[str, Any]:
    executable = check_mediainfo_available()
    completed = subprocess.run(
        [executable, "--Output=JSON", str(Path(path))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"mediainfo failed with exit code {completed.returncode}: {completed.stderr.strip()}")
    return json.loads(completed.stdout or "{}")


def probe_mediainfo_optional(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return probe_mediainfo(path), None
    except Exception as exc:  # noqa: BLE001 - optional metadata should not stop pipeline.
        return None, str(exc)

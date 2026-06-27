"""Update check helpers for packaged MediaQC releases."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from . import __version__


DEFAULT_RELEASE_API = "https://api.github.com/repos/tasselscrystal334-cyber/Media-Prep-Platform/releases/latest"


@dataclass(slots=True)
class UpdateInfo:
    current_version: str
    latest_version: str | None
    update_available: bool
    release_url: str | None = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "update_available": self.update_available,
            "release_url": self.release_url,
            "message": self.message,
        }


def check_for_updates(api_url: str = DEFAULT_RELEASE_API, timeout: int = 5) -> UpdateInfo:
    try:
        with urllib.request.urlopen(api_url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return UpdateInfo(
            current_version=__version__,
            latest_version=None,
            update_available=False,
            message=f"Unable to check for updates: {exc}",
        )

    latest = normalize_version(str(payload.get("tag_name") or payload.get("name") or ""))
    current = normalize_version(__version__)
    available = bool(latest and compare_versions(latest, current) > 0)
    return UpdateInfo(
        current_version=__version__,
        latest_version=latest or None,
        update_available=available,
        release_url=payload.get("html_url"),
        message="Update available." if available else "MediaQC is up to date.",
    )


def normalize_version(value: str) -> str:
    match = re.search(r"(\d+(?:\.\d+){0,3})", value)
    return match.group(1) if match else ""


def compare_versions(left: str, right: str) -> int:
    left_parts = _version_tuple(left)
    right_parts = _version_tuple(right)
    if left_parts > right_parts:
        return 1
    if left_parts < right_parts:
        return -1
    return 0


def _version_tuple(value: str) -> tuple[int, ...]:
    parts = [int(part) for part in normalize_version(value).split(".") if part != ""]
    return tuple(parts + [0] * (4 - len(parts)))

"""Built-in project profile loading."""

from __future__ import annotations

import sys
from pathlib import Path

from .rules import ProjectRules, load_rules

PROFILE_ALIASES = {
    "led4k": "LED_4K.yaml",
    "led_4k": "LED_4K.yaml",
    "led8k": "LED_8K.yaml",
    "led_8k": "LED_8K.yaml",
    "millumin": "Millumin.yaml",
    "disguise": "Disguise.yaml",
    "pixera": "Pixera.yaml",
    "touchdesigner": "TouchDesigner.yaml",
    "td": "TouchDesigner.yaml",
    "notch": "Notch.yaml",
}


def load_profile(name: str) -> tuple[ProjectRules, Path]:
    """Load a built-in profile by CLI-friendly name."""

    profile_path = resolve_profile_path(name)
    return load_rules(profile_path), profile_path


def resolve_profile_path(name: str) -> Path:
    normalized = name.strip().casefold().replace("-", "_").replace(" ", "_")
    filename = PROFILE_ALIASES.get(normalized)
    if filename is None:
        available = ", ".join(sorted(PROFILE_ALIASES))
        raise ValueError(f"Unknown profile '{name}'. Available profiles: {available}")

    for profile_dir in _profile_dirs():
        candidate = profile_dir / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Profile file was not found: {filename}")


def list_profiles() -> list[str]:
    return sorted(set(PROFILE_ALIASES))


def _profile_dirs() -> list[Path]:
    package_root = Path(__file__).resolve().parents[1]
    return [
        Path.cwd() / "profiles",
        package_root / "profiles",
        Path(sys.prefix) / "profiles",
    ]

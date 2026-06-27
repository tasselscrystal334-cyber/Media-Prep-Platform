"""User-facing product branding."""

from __future__ import annotations

from importlib import resources
from pathlib import Path


PRODUCT_NAME = "Loom"
CLI_NAME = "mediaqc"
GUI_BINARY_NAME = "Loom"


def icon_path() -> Path:
    """Return the packaged Loom icon path when available."""

    return Path(str(resources.files("mediaqc.assets").joinpath("loom_icon.svg")))

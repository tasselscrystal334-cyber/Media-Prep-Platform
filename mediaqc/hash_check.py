"""Hash helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path


def calculate_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Calculate SHA256 using streaming reads for large media files."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()

"""GUI helpers for scan result previews."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_RESULT_PREVIEW_LIMIT = 10


@dataclass(frozen=True)
class CsvPreview:
    headers: list[str]
    rows: list[list[str]]
    total_rows: int


def read_csv_preview(csv_path: Path, limit: int = DEFAULT_RESULT_PREVIEW_LIMIT) -> CsvPreview:
    """Read a small file-only preview from a scan CSV report."""

    path = Path(csv_path)
    if not path.exists():
        return CsvPreview(headers=[], rows=[], total_rows=0)

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows: list[list[str]] = []
        total_rows = 0
        for row in reader:
            if _is_directory_row(row):
                continue
            total_rows += 1
            if len(rows) < limit:
                rows.append([str(row.get(header, "")) for header in headers])
    return CsvPreview(headers=headers, rows=rows, total_rows=total_rows)


def _is_directory_row(row: dict[str, str]) -> bool:
    value = row.get("path") or ""
    if not value:
        return False
    try:
        return Path(value).is_dir()
    except OSError:
        return False

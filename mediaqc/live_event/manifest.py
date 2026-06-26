"""Manifest generation for live event delivery."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from mediaqc.scanner import scan_media_files
from mediaqc.hash_check import calculate_sha256
from mediaqc.probe import probe_media


MANIFEST_FIELDS = [
    "relative_path",
    "filename",
    "sha256",
    "size_bytes",
    "modified_at",
    "duration",
    "codec",
    "width",
    "height",
    "fps",
    "color_space",
    "status",
]


def build_manifest(project_path: Path, project_name: str | None = None, files: list[Any] | None = None) -> dict[str, Any]:
    root = Path(project_path).resolve()
    if files is None:
        files = []
        for media in scan_media_files(root):
            try:
                media.sha256 = calculate_sha256(media.path)
                media.ffprobe = probe_media(media.path)
            except Exception as exc:  # noqa: BLE001
                media.fail(str(exc))
            files.append(media)
    entries = [_entry(root, media) for media in files]
    return {
        "project_name": project_name or root.name,
        "project_path": str(root),
        "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        "media_count": len(entries),
        "files": entries,
    }


def write_manifest(manifest: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "manifest.json"
    csv_path = output / "manifest.csv"
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        for item in manifest["files"]:
            writer.writerow({field: item.get(field, "") for field in MANIFEST_FIELDS})
    return json_path, csv_path


def _entry(root: Path, media: Any) -> dict[str, Any]:
    ffprobe = getattr(media, "ffprobe", None) or {}
    video = _video_stream(ffprobe)
    stat = Path(media.path).stat() if Path(media.path).exists() else None
    return {
        "relative_path": str(Path(media.path).resolve().relative_to(root)),
        "filename": media.filename,
        "sha256": media.sha256,
        "size_bytes": media.size_bytes,
        "modified_at": datetime.fromtimestamp(stat.st_mtime).replace(microsecond=0).isoformat() if stat else None,
        "duration": _float_or_none(ffprobe.get("duration")),
        "codec": video.get("codec_name"),
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": video.get("avg_frame_rate"),
        "color_space": video.get("color_space"),
        "status": getattr(media, "rule_status", None) or media.status,
    }


def _video_stream(ffprobe: dict[str, Any]) -> dict[str, Any]:
    for stream in ffprobe.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return {}


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

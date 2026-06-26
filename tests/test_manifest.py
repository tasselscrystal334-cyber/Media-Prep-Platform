import csv
import json
from pathlib import Path

from mediaqc.live_event.manifest import build_manifest, write_manifest
from mediaqc.models import MediaFileResult


def test_build_and_write_manifest(tmp_path: Path) -> None:
    media_path = tmp_path / "Media" / "Opening.mov"
    media_path.parent.mkdir()
    media_path.write_bytes(b"abc")
    media = MediaFileResult(
        path=media_path,
        filename="Opening.mov",
        extension=".mov",
        size_bytes=3,
        sha256="sha",
    )
    media.ffprobe = {
        "duration": "60.0",
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "hap",
                "width": 3840,
                "height": 2160,
                "avg_frame_rate": "60/1",
                "color_space": "bt709",
            }
        ],
    }

    manifest = build_manifest(tmp_path, "LED Show", files=[media])
    json_path, csv_path = write_manifest(manifest, tmp_path / "reports")

    assert manifest["media_count"] == 1
    assert manifest["files"][0]["relative_path"] == "Media/Opening.mov"
    assert manifest["files"][0]["fps"] == 60.0
    assert json.loads(json_path.read_text(encoding="utf-8"))["project_name"] == "LED Show"
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig")))
    assert rows[0]["filename"] == "Opening.mov"

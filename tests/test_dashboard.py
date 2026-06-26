from pathlib import Path

from fastapi.testclient import TestClient

from mediaqc.dashboard import create_app
from mediaqc.database import MediaDatabase
from mediaqc.models import MediaFileResult


def test_dashboard_pages_and_api(tmp_path: Path) -> None:
    db_path = tmp_path / "media.db"
    media_path = tmp_path / "Opening.mov"
    media_path.write_bytes(b"movie")
    media = MediaFileResult(
        path=media_path,
        filename="Opening.mov",
        extension=".mov",
        size_bytes=media_path.stat().st_size,
        sha256="abc",
    )
    media.ffprobe = {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "hap",
                "width": 3840,
                "height": 2160,
                "avg_frame_rate": "60/1",
            }
        ]
    }

    with MediaDatabase(db_path) as db:
        project_id = db.get_or_create_project(tmp_path, "Dashboard Project")
        db.record_media(project_id, media)
        db.record_history(
            project_id=project_id,
            project_path=tmp_path,
            project_name="Dashboard Project",
            total_files=1,
            pass_count=1,
            warn_count=0,
            fail_count=0,
            rules_path=None,
            deep=False,
            html=True,
            scan_started="2026-06-26T12:00:00+00:00",
        )

    client = TestClient(create_app(db_path))

    overview = client.get("/")
    assert overview.status_code == 200
    assert "Overview" in overview.text
    assert "Recent Scan" in overview.text

    api_overview = client.get("/api/overview")
    assert api_overview.status_code == 200
    assert api_overview.json()["counts"]["Media"] == 1

    api_stats = client.get("/api/statistics")
    assert api_stats.status_code == 200
    assert api_stats.json()["codec"][0]["label"] == "hap"

    search = client.get("/search?q=Opening", headers={"HX-Request": "true"})
    assert search.status_code == 200
    assert "Opening.mov" in search.text

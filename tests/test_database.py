from pathlib import Path

from mediaqc.database import MediaDatabase
from mediaqc.models import MediaFileResult


def test_hash_cache_reuses_unmodified_file(tmp_path: Path) -> None:
    db_path = tmp_path / "media.db"
    media_path = tmp_path / "clip.mov"
    media_path.write_bytes(b"abc")
    calls = 0

    def calculate(path: Path) -> str:
        nonlocal calls
        calls += 1
        return f"hash-{path.read_bytes().decode()}"

    with MediaDatabase(db_path) as db:
        first_hash, first_cached = db.get_or_calculate_sha256(media_path, calculate)
        second_hash, second_cached = db.get_or_calculate_sha256(media_path, calculate)

    assert first_hash == "hash-abc"
    assert second_hash == "hash-abc"
    assert first_cached is False
    assert second_cached is True
    assert calls == 1


def test_hash_cache_recalculates_modified_file(tmp_path: Path) -> None:
    db_path = tmp_path / "media.db"
    media_path = tmp_path / "clip.mov"
    media_path.write_bytes(b"abc")

    with MediaDatabase(db_path) as db:
        first_hash, _ = db.get_or_calculate_sha256(media_path, lambda path: "hash-abc")
        media_path.write_bytes(b"abcd")
        second_hash, second_cached = db.get_or_calculate_sha256(media_path, lambda path: "hash-abcd")

    assert first_hash == "hash-abc"
    assert second_hash == "hash-abcd"
    assert second_cached is False


def test_record_media_and_find_duplicates(tmp_path: Path) -> None:
    db_path = tmp_path / "media.db"
    file_a = tmp_path / "a.mov"
    file_b = tmp_path / "b.mov"
    file_a.write_bytes(b"same")
    file_b.write_bytes(b"same")

    with MediaDatabase(db_path) as db:
        project_id = db.get_or_create_project(tmp_path, "Test Project")
        db.record_media(project_id, _media(file_a, "same-hash"))
        db.record_media(project_id, _media(file_b, "same-hash"))
        duplicates = db.duplicates()
        counts = db.database_counts()

    assert len(duplicates) == 1
    assert duplicates[0]["sha256"] == "same-hash"
    assert duplicates[0]["file_count"] == 2
    assert counts["Media"] == 2
    assert counts["Hash"] == 1


def test_record_history(tmp_path: Path) -> None:
    db_path = tmp_path / "media.db"

    with MediaDatabase(db_path) as db:
        project_id = db.get_or_create_project(tmp_path, "History Project")
        db.record_history(
            project_id=project_id,
            project_path=tmp_path,
            project_name="History Project",
            total_files=3,
            pass_count=2,
            warn_count=1,
            fail_count=0,
            rules_path=None,
            deep=False,
            html=True,
            scan_started="2026-06-26T12:00:00",
        )
        history = db.history()

    assert len(history) == 1
    assert history[0]["project_name"] == "History Project"
    assert history[0]["total_files"] == 3
    assert history[0]["html"] == 1


def test_prune_missing_media_removes_deleted_paths(tmp_path: Path) -> None:
    db_path = tmp_path / "media.db"
    file_a = tmp_path / "a.mov"
    file_b = tmp_path / "b.mov"
    file_a.write_bytes(b"a")
    file_b.write_bytes(b"b")

    with MediaDatabase(db_path) as db:
        project_id = db.get_or_create_project(tmp_path, "Watch Project")
        db.record_media(project_id, _media(file_a, "hash-a"))
        db.record_media(project_id, _media(file_b, "hash-b"))
        file_b.unlink()
        removed = db.prune_missing_media(project_id, {file_a})
        counts = db.database_counts()

    assert removed == 1
    assert counts["Media"] == 1
    assert counts["Hash"] == 1


def test_dashboard_queries(tmp_path: Path) -> None:
    db_path = tmp_path / "media.db"
    file_a = tmp_path / "a.mov"
    file_b = tmp_path / "b.mov"
    file_a.write_bytes(b"a")
    file_b.write_bytes(b"a")

    media_a = _media(file_a, "same-hash")
    media_a.ffprobe = {
        "streams": [{"codec_type": "video", "codec_name": "hap", "width": 3840, "height": 2160, "avg_frame_rate": "60/1"}]
    }
    media_b = _media(file_b, "same-hash")
    media_b.ffprobe = {
        "streams": [{"codec_type": "video", "codec_name": "hap", "width": 3840, "height": 2160, "avg_frame_rate": "60/1"}]
    }

    with MediaDatabase(db_path) as db:
        project_id = db.get_or_create_project(tmp_path, "Dashboard Project")
        db.record_media(project_id, media_a)
        db.record_media(project_id, media_b)
        overview = db.overview()
        stats = db.statistics()
        files = db.media_files("a.mov")

    assert overview["counts"]["Media"] == 2
    assert overview["duplicates"] == 1
    assert stats["codec"][0]["label"] == "hap"
    assert stats["resolution"][0]["label"] == "3840x2160"
    assert files[0]["filename"] == "a.mov"


def _media(path: Path, sha256: str) -> MediaFileResult:
    return MediaFileResult(
        path=path,
        filename=path.name,
        extension=path.suffix,
        size_bytes=path.stat().st_size,
        sha256=sha256,
    )

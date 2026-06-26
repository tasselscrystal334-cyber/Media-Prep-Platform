from pathlib import Path

from mediaqc.live_event.integrity import verify_manifest
from mediaqc.live_event.manifest import build_manifest, write_manifest
from mediaqc.models import MediaFileResult


def test_verify_manifest_passes_matching_project(tmp_path: Path) -> None:
    media_path = tmp_path / "Media" / "Opening.mov"
    media_path.parent.mkdir()
    media_path.write_bytes(b"abc")
    media = _media(media_path, "sha")
    media.sha256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    manifest = build_manifest(tmp_path, files=[media])
    json_path, _ = write_manifest(manifest, tmp_path / "reports")

    report = verify_manifest(tmp_path, json_path)

    assert report.status == "PASS"


def test_verify_manifest_fails_missing_or_modified(tmp_path: Path) -> None:
    media_path = tmp_path / "Media" / "Opening.mov"
    media_path.parent.mkdir()
    media_path.write_bytes(b"abc")
    media = _media(media_path, "bad")
    manifest = build_manifest(tmp_path, files=[media])
    json_path, _ = write_manifest(manifest, tmp_path / "reports")
    media_path.write_bytes(b"changed")

    report = verify_manifest(tmp_path, json_path)

    assert report.status == "FAIL"
    assert report.modified_files


def test_verify_manifest_warns_new_duplicate_and_naming(tmp_path: Path) -> None:
    media_path = tmp_path / "Media" / "Opening.mov"
    extra = tmp_path / "Media" / "中文 文件.mov"
    media_path.parent.mkdir()
    media_path.write_bytes(b"abc")
    extra.write_bytes(b"abc")
    media = _media(media_path, "sha")
    media.sha256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    manifest = build_manifest(tmp_path, files=[media])
    json_path, _ = write_manifest(manifest, tmp_path / "reports")

    report = verify_manifest(tmp_path, json_path)

    assert report.status == "WARN"
    assert report.new_files
    assert report.duplicate_files
    assert report.naming_warnings


def _media(path: Path, sha256: str) -> MediaFileResult:
    return MediaFileResult(
        path=path,
        filename=path.name,
        extension=path.suffix,
        size_bytes=path.stat().st_size,
        sha256=sha256,
    )

import json
import zipfile
from pathlib import Path

import pytest

from mediaqc.pipeline.compare import compare_sha256, write_compare_report
from mediaqc.pipeline.mediainfo import probe_mediainfo_optional
from mediaqc.pipeline.network import resolve_network_target
from mediaqc.pipeline.package import build_project_package
from mediaqc.pipeline.sync import run_pipeline_sync


def test_network_target_handles_mounted_local_path(tmp_path: Path) -> None:
    target = resolve_network_target(tmp_path)

    assert target.protocol == "local"
    assert target.mounted is True
    assert target.writable is True


def test_network_target_records_protocol_warning() -> None:
    target = resolve_network_target("smb:///Volumes/ShowNAS/Media")

    assert target.protocol == "smb"
    assert any("SMB destinations must be mounted" in warning for warning in target.warnings)


def test_mediainfo_optional_returns_warning_when_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    media = tmp_path / "a.mov"
    media.write_bytes(b"abc")
    monkeypatch.setattr("mediaqc.pipeline.mediainfo.shutil.which", lambda _: None)

    data, warning = probe_mediainfo_optional(media)

    assert data is None
    assert warning is not None
    assert "mediainfo was not found" in warning


def test_pipeline_sync_and_compare_reports(tmp_path: Path) -> None:
    source = tmp_path / "Media"
    destination = tmp_path / "Server"
    output = tmp_path / "Reports"
    media = source / "Opening.mov"
    source.mkdir()
    media.write_bytes(b"abc")

    result = run_pipeline_sync(source, destination, output, profile="disguise", collect_mediainfo=False)
    compare = compare_sha256(source, destination)
    compare_json, compare_csv = write_compare_report(compare, output)

    assert result.records[0].status == "SUCCESS"
    assert (destination / "Opening.mov").read_bytes() == b"abc"
    assert json.loads(result.transfer_json_path.read_text(encoding="utf-8"))["success"] == 1
    assert compare["match"] == 1
    assert compare_json.exists()
    assert compare_csv.exists()


def test_pipeline_compare_detects_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "Media"
    destination = tmp_path / "Server"
    source.mkdir()
    destination.mkdir()
    (source / "Opening.mov").write_bytes(b"abc")
    (destination / "Opening.mov").write_bytes(b"changed")

    report = compare_sha256(source, destination)

    assert report["mismatch"] == 1
    assert report["records"][0]["status"] == "MISMATCH"


def test_project_package_contains_manifest_and_media(tmp_path: Path) -> None:
    project = tmp_path / "Media"
    output = tmp_path / "Packages"
    project.mkdir()
    (project / "Opening.mov").write_bytes(b"abc")

    package = build_project_package(project, output, profile="notch")

    package_path = Path(package["package_path"])
    assert package_path.exists()
    with zipfile.ZipFile(package_path) as archive:
        names = set(archive.namelist())
    assert "reports/manifest.json" in names
    assert "Media/Opening.mov" in names
    assert "package_metadata.json" in names

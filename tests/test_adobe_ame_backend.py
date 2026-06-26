import csv
import json
from pathlib import Path

from mediaqc.processing.adobe_ame import (
    OFFICIAL_NOTCHLC_POLICY,
    AdobeMediaEncoderBackend,
    prepare_ame_notchlc_jobs,
)


def test_adobe_media_encoder_backend_never_builds_plugin_command() -> None:
    backend = AdobeMediaEncoderBackend()

    assert backend.supports("notchlc") is True
    try:
        backend.build_command(Path("input.mov"), Path("output.mov"), preset=None)
    except NotImplementedError as exc:
        assert "does not directly invoke Adobe plugins" in str(exc)
    else:
        raise AssertionError("AdobeMediaEncoderBackend must not build direct plugin commands.")


def test_prepare_ame_notchlc_jobs_writes_manifests_and_readme(tmp_path: Path) -> None:
    source = tmp_path / "Media" / "Opening.mov"
    source.parent.mkdir()
    source.write_bytes(b"fake")
    watch_folder = tmp_path / "AME_Watch"
    output_dir = tmp_path / "Encoded_NotchLC"

    payload = prepare_ame_notchlc_jobs(source.parent, watch_folder, output_dir)

    assert payload["total_jobs"] == 1
    assert payload["policy"] == OFFICIAL_NOTCHLC_POLICY
    assert (watch_folder / "Opening.mov").exists()
    json_data = json.loads((watch_folder / "ame_jobs.json").read_text(encoding="utf-8"))
    assert json_data["jobs"][0]["status"] == "READY"
    rows = list(csv.DictReader((watch_folder / "ame_jobs.csv").open(encoding="utf-8-sig")))
    assert rows[0]["mode"] == "copy"
    readme = (watch_folder / "README_AME_NOTCHLC.txt").read_text(encoding="utf-8")
    assert "does not call, load, inspect, patch, reverse engineer" in readme
    assert str(output_dir.resolve()) in readme


def test_prepare_ame_notchlc_jobs_preserves_relative_paths(tmp_path: Path) -> None:
    source = tmp_path / "Media" / "Scene" / "Opening.mov"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"fake")
    watch_folder = tmp_path / "AME_Watch"

    prepare_ame_notchlc_jobs(tmp_path / "Media", watch_folder, tmp_path / "Out", recursive=True)

    assert (watch_folder / "Scene" / "Opening.mov").exists()

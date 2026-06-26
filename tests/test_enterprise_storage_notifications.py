from pathlib import Path

import pytest

from mediaqc.enterprise.notifications import get_notification_backend
from mediaqc.enterprise.storage import get_storage_backend


def test_storage_backends_resolve_supported_uris(tmp_path: Path) -> None:
    local_file = tmp_path / "shot.mov"
    local_file.write_bytes(b"media")

    nas = get_storage_backend("nas").resolve(str(local_file))
    assert nas.exists is True
    assert nas.backend == "nas"

    assert get_storage_backend("s3").resolve("s3://bucket/shot.mov").exists is True
    assert get_storage_backend("azure").resolve("azure://container/shot.mov").exists is True
    assert get_storage_backend("google_drive").resolve("gdrive://folder/shot.mov").exists is True
    assert get_storage_backend("webdav").resolve("webdav://server/shot.mov").exists is True

    with pytest.raises(ValueError):
        get_storage_backend("unknown")


def test_notification_backends_build_dry_run_payloads() -> None:
    slack = get_notification_backend("slack").send("https://hooks.example/slack", "Scan complete", "MediaPrep")
    assert slack.status == "DRY_RUN"
    assert slack.payload["json"]["text"] == "MediaPrep: Scan complete"

    teams = get_notification_backend("teams").send("https://hooks.example/teams", "Scan failed")
    assert teams.payload["json"]["title"] == "MediaPrep"

    feishu = get_notification_backend("feishu").send("https://hooks.example/feishu", "Scan warning", "QC")
    assert feishu.payload["json"]["msg_type"] == "text"

    email = get_notification_backend("email").send("ops@example.com", "Scan complete")
    assert "ops@example.com" in email.payload["message"]

    with pytest.raises(ValueError):
        get_notification_backend("sms")

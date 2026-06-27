import subprocess
import sys

from mediaqc.editions import COMMUNITY_EDITION, ENTERPRISE_EDITION, get_edition_matrix


def test_edition_matrix_defines_community_and_enterprise_boundaries() -> None:
    editions = get_edition_matrix()

    assert editions == (COMMUNITY_EDITION, ENTERPRISE_EDITION)
    assert COMMUNITY_EDITION.license_name == "Apache License 2.0"
    assert "FFmpeg integration" in COMMUNITY_EDITION.features
    assert "Batch transcoding" in COMMUNITY_EDITION.features
    assert ENTERPRISE_EDITION.license_name == "Commercial License"
    assert "LDAP/AD integration" in ENTERPRISE_EDITION.features
    assert "Render Farm management" in ENTERPRISE_EDITION.features


def test_editions_cli_outputs_license_boundaries() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mediaqc.cli", "editions"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Community Edition" in result.stdout
    assert "Apache License 2.0" in result.stdout
    assert "Enterprise Edition" in result.stdout
    assert "Commercial License" in result.stdout
    assert "Render Farm management" in result.stdout

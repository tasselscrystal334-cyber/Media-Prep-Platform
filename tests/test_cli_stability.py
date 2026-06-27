import subprocess
import sys

from mediaqc import __version__


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mediaqc.cli", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_version_command() -> None:
    result = run_cli("version")

    assert result.returncode == 0
    assert __version__ in result.stdout


def test_root_doctor_alias() -> None:
    result = run_cli("doctor")

    assert result.returncode == 0
    assert "Loom Tools Doctor" in result.stdout


def test_install_check_json() -> None:
    result = run_cli("tools", "install-check", "--json")

    assert result.returncode in {0, 1}
    assert '"checks"' in result.stdout


def test_update_check_handles_unavailable_endpoint() -> None:
    result = run_cli("update", "check", "--api-url", "http://127.0.0.1:9/latest", "--timeout", "1", "--json")

    assert result.returncode == 0
    assert "Unable to check for updates" in result.stdout

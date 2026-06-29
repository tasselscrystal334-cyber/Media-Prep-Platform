import shutil
import stat
import zipfile
from pathlib import Path

from mediaqc.processing.tool_installer import application_tools_plugins_dir, default_tool_install_dir, ensure_ffmpeg_bundle_installed


def test_default_tool_install_dir_uses_software_tools_plugins(monkeypatch) -> None:
    monkeypatch.delenv("LOOM_TOOLS_DIR", raising=False)
    monkeypatch.delenv("MEDIAQC_FFMPEG_DIR", raising=False)

    install_dir = default_tool_install_dir()

    assert install_dir == application_tools_plugins_dir() / "ffmpeg"
    assert install_dir.parts[-3:] == ("tools", "plugins", "ffmpeg")


def test_ensure_ffmpeg_bundle_installed_from_zip(monkeypatch, tmp_path: Path) -> None:
    package = tmp_path / "ffmpeg.zip"
    source_dir = tmp_path / "source" / "ffmpeg" / "bin"
    source_dir.mkdir(parents=True)
    for name in ("ffmpeg", "ffprobe", "ffplay"):
        tool = source_dir / name
        tool.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
        tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
    with zipfile.ZipFile(package, "w") as archive:
        for tool in source_dir.iterdir():
            archive.write(tool, tool.relative_to(tmp_path / "source"))

    install_dir = tmp_path / "installed"
    monkeypatch.setenv("LOOM_TOOLS_DIR", str(install_dir))
    monkeypatch.setenv("LOOM_FFMPEG_PACKAGE_URL", "https://example.test/ffmpeg.zip")
    monkeypatch.delenv("LOOM_DISABLE_TOOL_DOWNLOAD", raising=False)
    monkeypatch.delenv("MEDIAQC_DISABLE_TOOL_DOWNLOAD", raising=False)

    def fake_urlretrieve(_url: str, destination: Path) -> tuple[str, object | None]:
        shutil.copy2(package, destination)
        return str(destination), None

    monkeypatch.setattr("mediaqc.processing.tool_installer.urllib.request.urlretrieve", fake_urlretrieve)

    result = ensure_ffmpeg_bundle_installed()

    assert result.downloaded is True
    assert result.install_dir == install_dir
    for name in ("ffmpeg", "ffprobe", "ffplay"):
        assert (install_dir / name).exists()


def test_ensure_ffmpeg_bundle_reuses_existing_tools(monkeypatch, tmp_path: Path) -> None:
    install_dir = tmp_path / "installed"
    install_dir.mkdir()
    for name in ("ffmpeg", "ffprobe", "ffplay"):
        tool = install_dir / name
        tool.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
        tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("LOOM_TOOLS_DIR", str(install_dir))

    result = ensure_ffmpeg_bundle_installed()

    assert result.downloaded is False
    assert result.install_dir == install_dir

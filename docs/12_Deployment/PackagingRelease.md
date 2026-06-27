# Packaging Release

## Purpose

Document the V2.0 packaging and release system for cross-platform MediaQC distributions.

## Overview

MediaQC supports source installs, editable development installs, PyInstaller CLI/GUI bundles, Docker service images, and GitHub Actions release assets.

## Architecture

Packaging files live under `packaging/`. PyInstaller specs build `mediaqc` and `mediaqc-gui` bundles. Docker files package the enterprise API service. GitHub Actions build Windows, macOS, and Linux archives and publish release assets for tagged versions.

## Workflow

Developers install with `pip install -e .`, run tests, build platform bundles with the scripts in `packaging/scripts/`, and publish release assets from `dist_release/`. Release scripts generate archives, `SHA256SUMS.txt`, and `release_notes.md`.

## Dependencies

- Python 3.11+
- PyInstaller for desktop/CLI bundles
- Docker for server images
- Optional PySide6 for GUI bundles
- Optional enterprise dependencies for server stacks
- External or bundled FFmpeg tools

## Configuration

FFmpeg tools are resolved in this order:

1. `MEDIAQC_FFMPEG_PATH`, `MEDIAQC_FFPROBE_PATH`, or `MEDIAQC_FFPLAY_PATH`
2. `MEDIAQC_FFMPEG_DIR`
3. PyInstaller bundle folders such as `tools/`
4. `tools/` beside the executable
5. System `PATH`

## Example

```bash
python -m pip install -e ".[release]"
bash packaging/scripts/build_macos.sh
python packaging/scripts/make_release.py --platform macos --dist dist --output dist_release
```

## Known Limitations

PyInstaller bundles do not download FFmpeg automatically. Operators must install FFmpeg externally or place licensed binaries in a `tools/` folder before packaging.

## Future Improvements

Add code signing, notarization, Windows installer generation, package manager publishing, and Docker registry publishing.

## Related Modules

- `packaging/pyinstaller/mediaqc_cli.spec`
- `packaging/pyinstaller/mediaqc_gui.spec`
- `packaging/scripts/make_release.py`
- `mediaqc/processing/ffmpeg_runner.py`
- `.github/workflows/release.yml`

## Revision History

- Documentation version: 2.0
- Last updated: 2026-06-27

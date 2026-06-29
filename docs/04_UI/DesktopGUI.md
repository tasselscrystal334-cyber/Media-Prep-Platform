# Desktop GUI

## Purpose

Document the Loom desktop GUI structure, first-run experience, and packaging-facing UI requirements.

## Overview

The desktop GUI is a PySide6 application named Loom. It opens with a light welcome cover that shows the product icon, version number, New/Open/Recent entry points, and a translucent glass-style panel over a light gray background. The main workspace uses a soft light, low-contrast gray and white engineering layout: left project/rules/history navigation, center scan queue, and right preview/log panels.

## Architecture

GUI code lives under `mediaqc/gui/`.

- `app.py` creates the Qt application, sets Loom branding, shows the early splash screen, and opens the main window.
- `main_window.py` owns menus, welcome cover, workspace layout, drag/drop project selection, scan queue, progress, cancellation, logs, and report opening.
- `theme.py` defines the light stylesheet.
- `workers.py` keeps scan execution off the main thread and lazily imports heavier scan/report modules after the operator starts a scan.
- `mediaqc/assets/loom_icon.svg` provides the packaged icon asset.

## Workflow

Operators open Loom, choose New, Open, or Recent, then scan one or more media folders. On first launch, Loom checks `ffmpeg`, `ffprobe`, and `ffplay`; if any are missing, the GUI prompts before installing them into `tools/plugins/ffmpeg`. Reports can be exported as JSON, CSV, HTML, and PDF. The menu bar exposes Loom, File, Edit, View, Presets, Window, and Help menus.

## Dependencies

- Python 3.11+
- PySide6
- FFmpeg and FFprobe for media analysis
- Optional FFplay and MediaInfo for preview and richer metadata

## Configuration

The GUI uses the same rules, profiles, presets, and report output paths as the CLI. The packaged application may use external tools from `PATH`, explicit `MEDIAQC_*` environment variables, or the bundled `tools/plugins/ffmpeg` folder. Preferences > Basic includes an Install / Repair FFmpeg Tools action.

## Example

```bash
python -m pip install -e ".[gui]"
loom-gui
```

Packaged releases should expose the desktop application as `Loom`, without a GUI suffix in the download name.

## Known Limitations

PyInstaller and macOS first-launch security checks can still add startup overhead before Python code runs. Loom shows a splash as soon as Qt initializes, but platform-level launch latency may still be visible on the first open.

## Future Improvements

- Add a persistent recent-project store.
- Add a GUI tools doctor panel for FFmpeg, FFprobe, FFplay, MediaInfo, and official vendor encoders.
- Add native app icon formats for signed macOS and Windows installers.

## Related Modules

- `mediaqc/gui/app.py`
- `mediaqc/gui/main_window.py`
- `mediaqc/gui/theme.py`
- `mediaqc/gui/workers.py`
- `mediaqc/assets/loom_icon.svg`
- `packaging/pyinstaller/mediaqc_gui.spec`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29

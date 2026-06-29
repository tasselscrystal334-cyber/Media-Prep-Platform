# Desktop GUI

## Purpose

Document the Loom desktop GUI structure, first-run experience, and packaging-facing UI requirements.

## Overview

The desktop GUI is a PySide6 application named Loom. It opens with a light welcome cover that shows the product icon, version number, New/Open/Recent entry points, and a translucent glass-style panel over a light gray background. The main workspace uses a soft light, low-contrast gray and white engineering layout inspired by professional transcoding tools: an in-window Loom menu bar, a responsive action toolbar, imported media file lists, direct output settings, output file planning, and paged source/output/log views.

## Architecture

GUI code lives under `mediaqc/gui/`.

- `app.py` creates the Qt application, sets Loom branding, shows the early splash screen, and opens the main window.
- `main_window.py` owns the in-window menu bar, welcome cover, workspace layout, drag/drop media import, source preview filtering, progress, cancellation, logs, playback, transcode/export, and report opening.
- `theme.py` defines the light stylesheet.
- `workers.py` keeps scan execution off the main thread and lazily imports heavier scan/report modules after the operator starts a scan.
- `mediaqc/assets/loom_icon.svg` provides the packaged icon asset.

## Workflow

Operators open Loom, choose New, Open, or Recent, then import one file, multiple files, a folder, or drag media into the file list. On first launch, Loom checks `ffmpeg`, `ffprobe`, and `ffplay`; if any are missing, the GUI prompts before installing them into `tools/plugins/ffmpeg`. The primary modules are decode, analysis, playback, SHA256 verification, and transcode/export. Output settings are direct controls for Codec, Frame Rate, Proxy, and Format; Format defaults to MOV and audio defaults to copying the original audio. Output files default to each source file's folder unless a custom destination is selected. Compression and transcode workflows use right-side Source Preview, Output Preview, and Logs pages. Play opens the selected file in a separate fullscreen FFplay window, and crop controls can be applied as an FFplay crop filter. Rules remain configurable through YAML files under `config/` rather than as a main workspace panel.

## Dependencies

- Python 3.11+
- PySide6
- FFmpeg and FFprobe for media analysis
- Optional FFplay and MediaInfo for preview and richer metadata

## Configuration

The GUI uses the same rules, profiles, presets, and report output paths as the CLI, but rule editing remains a configuration-file workflow in `config/`. The packaged application may use external tools from `PATH`, explicit `MEDIAQC_*` environment variables, or the bundled `tools/plugins/ffmpeg` folder. Preferences > Basic includes an Install / Repair FFmpeg Tools action.

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

- Documentation version: 1.8
- Last updated: 2026-06-29

# Bundled Tools

## Purpose

Document the optional external tools that may be placed beside Loom release binaries.

## Overview

The `tools/` folder is intentionally included in release bundles as an operator-controlled location for external command-line tools. Loom first uses tools on `PATH` or explicit environment variables, then bundled tools, and can automatically download the FFmpeg tool bundle into the user tools cache when `ffmpeg`, `ffprobe`, or `ffplay` is missing.

## Architecture

Tool discovery is handled by `mediaqc/processing/ffmpeg_runner.py`. Download and install behavior is isolated in `mediaqc/processing/tool_installer.py`.

## Workflow

Place licensed platform binaries in this folder before packaging, copy them into the installed release folder after download, or run:

```bash
mediaqc tools install-ffmpeg
```

Recommended candidates:

- `ffmpeg`
- `ffprobe`
- `ffplay`
- `mediainfo`
- Official NotchLC encoder or SDK command-line tool, when legally obtained
- Vendor-specific verification tools used by a show pipeline

## Dependencies

External tools must match the target operating system and CPU architecture. Operators are responsible for tool licensing and redistribution rights.

## Configuration

Environment overrides:

- `MEDIAQC_FFMPEG_PATH`
- `MEDIAQC_FFPROBE_PATH`
- `MEDIAQC_FFPLAY_PATH`
- `MEDIAQC_FFMPEG_DIR`
- `LOOM_TOOLS_DIR`
- `LOOM_FFMPEG_PACKAGE_URL`
- `LOOM_DISABLE_TOOL_DOWNLOAD=1`

## Example

```text
Loom/
  Loom
  tools/
    ffmpeg
    ffprobe
    ffplay
```

## Known Limitations

Release scripts do not download FFmpeg or vendor tools automatically. At runtime, Loom can download FFmpeg-family tools into the user cache unless automatic downloads are disabled.

## Future Improvements

- Add a GUI tools doctor panel.
- Add platform-specific tool bundle recipes.

## Related Modules

- `mediaqc/processing/ffmpeg_runner.py`
- `mediaqc/processing/tool_installer.py`
- `mediaqc/diagnostics.py`
- `packaging/pyinstaller/mediaqc_gui.spec`
- `packaging/scripts/make_release.py`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29

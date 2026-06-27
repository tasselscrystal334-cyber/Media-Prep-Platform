# Bundled Tools

## Purpose

Document the optional external tools that may be placed beside Loom release binaries.

## Overview

The `tools/` folder is intentionally included in release bundles as an operator-controlled location for external command-line tools. Loom does not require bundled tools when FFmpeg is already available on `PATH`, but packaged deployments can place supported binaries here for portable offline workflows.

## Architecture

Tool discovery is handled by `mediaqc/processing/ffmpeg_runner.py`. The resolver checks explicit environment variables, `MEDIAQC_FFMPEG_DIR`, bundled release folders, a `tools/` directory beside the executable, and finally the system `PATH`.

## Workflow

Place licensed platform binaries in this folder before packaging, or copy them into the installed release folder after download.

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

Release scripts do not download FFmpeg or vendor tools automatically. Empty `tools/` folders are valid and mean Loom will use environment variables or `PATH`.

## Future Improvements

- Add a GUI tools doctor panel.
- Add optional first-run prompts when FFmpeg tools are missing.
- Add platform-specific tool bundle recipes.

## Related Modules

- `mediaqc/processing/ffmpeg_runner.py`
- `mediaqc/diagnostics.py`
- `packaging/pyinstaller/mediaqc_gui.spec`
- `packaging/scripts/make_release.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

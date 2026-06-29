# FFplay

## Purpose

Reserve codec documentation space for FFplay preview workflows.

## Overview

FFplay is a default Loom media tool module invoked by `mediaqc play` for operator preview.

## Architecture

FFplay command construction lives in `mediaqc/processing/ffplay.py` and execution is routed through `mediaqc/processing/ffmpeg_runner.py`. If missing, Loom can install the full FFmpeg tool bundle through `mediaqc/processing/tool_installer.py`.

## Workflow

Operators can preview media with loop, mute, start time, scale, and timecode options.

## Dependencies

- `ffplay` from a full FFmpeg package on `PATH`, bundled tools, or the software-local `tools/plugins/ffmpeg` directory.

## Configuration

No persistent configuration is required. CLI options control preview behavior. Set `MEDIAQC_FFPLAY_PATH` for an explicit binary or `LOOM_DISABLE_TOOL_DOWNLOAD=1` to disable automatic downloads.

## Example

```bash
mediaqc play ./Media/Opening.mov --loop --mute --scale 0.5 --timecode
```

## Known Limitations

FFplay availability depends on the local FFmpeg package. Automatic downloads require network access and upstream package availability.

## Future Improvements

Add LUT and color-check preview modes.

## Related Modules

- `mediaqc/processing/ffplay.py`
- `mediaqc/processing/ffmpeg_runner.py`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29

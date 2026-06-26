# FFplay

## Purpose

Reserve codec documentation space for FFplay preview workflows.

## Overview

FFplay is invoked by `mediaqc play` for operator preview.

## Architecture

FFplay command construction lives in `mediaqc/processing/ffplay.py` and execution is routed through `mediaqc/processing/ffmpeg_runner.py`.

## Workflow

Operators can preview media with loop, mute, start time, scale, and timecode options.

## Dependencies

- Optional `ffplay` binary from a full FFmpeg package.

## Configuration

No persistent configuration is required. CLI options control preview behavior.

## Example

```bash
mediaqc play ./Media/Opening.mov --loop --mute --scale 0.5 --timecode
```

## Known Limitations

FFplay availability depends on the local FFmpeg package.

## Future Improvements

Add LUT and color-check preview modes.

## Related Modules

- `mediaqc/processing/ffplay.py`
- `mediaqc/processing/ffmpeg_runner.py`

## Revision History

- Documentation version: 0.95
- Last updated: 2026-06-27

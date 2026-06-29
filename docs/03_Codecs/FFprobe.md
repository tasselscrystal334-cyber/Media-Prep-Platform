# FFprobe

## Purpose

Document how Loom extracts media metadata.

## Overview

`ffprobe` is a default Loom media tool module. It provides container and stream metadata used by reports, validators, profiles, live event checks, and the dashboard.

## Architecture

Metadata is normalized in `mediaqc/probe.py`. Tool path resolution and automatic installation are handled by `mediaqc/processing/ffmpeg_runner.py` and `mediaqc/processing/tool_installer.py`.

## Workflow

The command is:

```bash
ffprobe -v quiet -print_format json -show_format -show_streams input_file
```

## Dependencies

- `ffprobe` on `PATH`, in bundled tools, or in the software-local `tools/plugins/ffmpeg` directory

## Configuration

Set `MEDIAQC_FFPROBE_PATH` for an explicit binary or `LOOM_DISABLE_TOOL_DOWNLOAD=1` to disable automatic FFmpeg bundle downloads.

## Example

Stream fields include codec, width, height, frame rate, pixel format, color space, and color range.

## Known Limitations

Some image and invalid media files may produce incomplete metadata.

## Future Improvements

Preserve more raw ffprobe fields for advanced analytics.

## Related Modules

- `mediaqc/probe.py`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29

# FFprobe

## Purpose

Document how MediaPrepTool extracts media metadata.

## Overview

`ffprobe` provides container and stream metadata used by reports, validators, profiles, live event checks, and the dashboard.

## Architecture

Metadata is normalized in `mediaqc/probe.py`.

## Workflow

The command is:

```bash
ffprobe -v quiet -print_format json -show_format -show_streams input_file
```

## Dependencies

- `ffprobe` on `PATH`

## Configuration

No standalone FFprobe config.

## Example

Stream fields include codec, width, height, frame rate, pixel format, color space, and color range.

## Known Limitations

Some image and invalid media files may produce incomplete metadata.

## Future Improvements

Preserve more raw ffprobe fields for advanced analytics.

## Related Modules

- `mediaqc/probe.py`

## Revision History

- Documentation version: 0.95

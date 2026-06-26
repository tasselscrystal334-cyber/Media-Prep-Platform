# FFmpeg

## Purpose

Document how MediaPrepTool uses FFmpeg.

## Overview

FFmpeg is used for decode-level deep analysis through `mediaqc/deep_analysis.py`.

## Architecture

The deep analysis command is:

```bash
ffmpeg -v error -i input -f null -
```

## Workflow

Enable deep analysis with:

```bash
mediaqc scan ./Media --deep
```

## Dependencies

- `ffmpeg` on `PATH`

## Configuration

No FFmpeg-specific YAML configuration currently exists.

## Example

Decode errors are converted into `decode_report` fields.

## Known Limitations

Deep analysis fully decodes files and can be slow on large media.

## Future Improvements

Expose timeout and stream selection configuration.

## Related Modules

- `mediaqc/deep_analysis.py`

## Revision History

- Documentation version: 0.95

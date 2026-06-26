# FFmpeg

## Purpose

Document how MediaPrepTool uses FFmpeg.

## Overview

FFmpeg is used for decode-level deep analysis, transcode jobs, subtitle operations, logo overlay rendering, and environment diagnostics.

## Architecture

The deep analysis command is:

```bash
ffmpeg -v error -i input -f null -
```

Processing commands are routed through `mediaqc/processing/ffmpeg_runner.py`, which keeps command lists shell-free and path-safe.

## Workflow

Enable deep analysis with:

```bash
mediaqc scan ./Media --deep
mediaqc tools doctor
mediaqc transcode input.mov --preset h264_preview --output ./preview
```

## Dependencies

- `ffmpeg` on `PATH`
- Optional codec libraries such as HAP, ProRes, libx264, libx265, or external NotchLC backends.

## Configuration

Transcode presets are YAML files under `config/transcode_presets/`. Optional encoder backends are configured in `config/encoder_backends.yaml`.

## Example

Decode errors are converted into `decode_report` fields.

## Known Limitations

Deep analysis fully decodes files and can be slow on large media.

## Future Improvements

Expose timeout, stream selection, hardware acceleration, and preset validation policy.

## Related Modules

- `mediaqc/deep_analysis.py`
- `mediaqc/processing/ffmpeg_runner.py`
- `mediaqc/processing/transcode.py`
- `mediaqc/processing/subtitles.py`
- `mediaqc/processing/overlay.py`

## Revision History

- Documentation version: 0.95
- Last updated: 2026-06-27

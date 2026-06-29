# FFmpeg

## Purpose

Document how Loom uses FFmpeg.

## Overview

FFmpeg is a default Loom media tool module. It is used for decode-level deep analysis, transcode jobs, subtitle operations, logo overlay rendering, and environment diagnostics.

## Architecture

The deep analysis command is:

```bash
ffmpeg -v error -i input -f null -
```

Processing commands are routed through `mediaqc/processing/ffmpeg_runner.py`, which keeps command lists shell-free and path-safe. If `ffmpeg`, `ffprobe`, or `ffplay` is missing, `mediaqc/processing/tool_installer.py` can download the full FFmpeg tool bundle into the software-local `tools/plugins/ffmpeg` directory.

## Workflow

Enable deep analysis with:

```bash
mediaqc scan ./Media --deep
mediaqc tools doctor
mediaqc tools install-ffmpeg
mediaqc transcode input.mov --preset h264_preview --output ./preview
```

## Dependencies

- `ffmpeg` on `PATH`, in bundled tools, or in the software-local `tools/plugins/ffmpeg` directory
- Optional codec libraries such as HAP, ProRes, libx264, libx265, or external NotchLC backends.

## Configuration

Transcode presets are YAML files under `config/transcode_presets/`. Optional encoder backends are configured in `config/encoder_backends.yaml`. Set `LOOM_DISABLE_TOOL_DOWNLOAD=1` to disable runtime FFmpeg downloads.

## Example

Decode errors are converted into `decode_report` fields.

## Known Limitations

Deep analysis fully decodes files and can be slow on large media. Automatic FFmpeg downloads require network access and operator acceptance of upstream FFmpeg package licensing.

## Future Improvements

Expose timeout, stream selection, hardware acceleration, and preset validation policy.

## Related Modules

- `mediaqc/deep_analysis.py`
- `mediaqc/processing/ffmpeg_runner.py`
- `mediaqc/processing/transcode.py`
- `mediaqc/processing/subtitles.py`
- `mediaqc/processing/overlay.py`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29

# Processing

## Purpose

Document transcode, subtitle, logo overlay, dry-run, batch job, logging, and processing report behavior.

## Overview

Processing commands create explicit jobs with input path, output path, preset, command, status, timing, error, and log path. Jobs can be run one at a time by default or with an explicit worker count.

## Architecture

Processing modules live under `mediaqc/processing/`. FFmpeg execution is centralized in `ffmpeg_runner.py`; presets are YAML-driven; NotchLC encoding is an optional backend; job execution and report writing are centralized in `jobs.py`.
Adobe Media Encoder NotchLC workflows are prepared through Watch Folders only and never by loading Adobe plugin binaries.

## Workflow

Use `mediaqc tools doctor` before processing on a show machine. Use `--dry-run` to inspect commands before rendering. Batch operations should continue after individual failures and write `job_report.json` plus `job_report.csv`.

## Dependencies

Python 3.11+, FFmpeg tools, PyYAML, Rich, and optional external encoder backends such as a NotchLC encoder.

## Configuration

Transcode presets live in `config/transcode_presets/`. Optional external encoders are configured in `config/encoder_backends.yaml`.

## Example

```bash
mediaqc transcode ./Media --preset h264_preview --output ./preview --recursive --dry-run
mediaqc notchlc prepare ./Media --watch-folder ./AME_Watch --output ./Encoded_NotchLC
mediaqc subtitle input.mov --subtitle captions.srt --mode soft --output output.mp4
mediaqc logo input.mov --logo logo.png --position top-right --output output_logo.mp4
```

## Known Limitations

Processing quality depends on installed FFmpeg encoders and optional external encoder tools. NotchLC encoding is not assumed to be available.
NotchLC Adobe plugin integration is intentionally limited to official AME/Premiere/After Effects workflows and user-provided official SDK/tools.

## Future Improvements

Add GPU encoding policies, preset compatibility matrices, queue persistence, cancellation, and GUI integration.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/processing/ffmpeg_runner.py`
- `mediaqc/processing/transcode.py`
- `mediaqc/processing/jobs.py`
- `mediaqc/processing/adobe_ame.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

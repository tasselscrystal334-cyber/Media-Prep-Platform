# LED Show 6400x2000 Example

## Purpose

Provide a copyable example project for live-event Loom scans.

## Overview

This example targets a 6400x2000 LED canvas split across two processor inputs. Place media files in `Media/`, then run the commands below from the repository root.

## Architecture

The example mirrors a show folder: media files, versioned YAML configuration, generated reports, and an operator runbook.

## Workflow

```bash
mediaqc tools install-check
mediaqc scan examples/LED_Show_6400x2000/Media \
  --rules examples/LED_Show_6400x2000/config/project_rules.yaml \
  --output-spec examples/LED_Show_6400x2000/config/output_spec.yaml \
  --canvas-spec examples/LED_Show_6400x2000/config/canvas_spec.yaml \
  --output examples/LED_Show_6400x2000/reports \
  --html \
  --manifest
mediaqc manifest examples/LED_Show_6400x2000/Media --output examples/LED_Show_6400x2000/reports
mediaqc verify examples/LED_Show_6400x2000/Media --manifest examples/LED_Show_6400x2000/reports/manifest.json
```

## Dependencies

- Loom CLI (`mediaqc` command)
- FFmpeg with ffprobe
- Media files copied into `Media/`

## Configuration

- `config/project_rules.yaml`
- `config/output_spec.yaml`
- `config/canvas_spec.yaml`

## Example

The expected full-canvas media resolution is `6400x2000` at `60fps` with BT.709 color space.

## Known Limitations

The repository does not include large media files. Add your own `.mov`, `.mp4`, `.mxf`, `.mkv`, `.avi`, image, or audio assets before scanning.

## Future Improvements

Add downloadable small test media fixtures once repository asset policy is finalized.

## Related Modules

- `mediaqc/live_event/`
- `mediaqc/report.py`
- `mediaqc/cli.py`

## Revision History

- Documentation version: 2.0
- Last updated: 2026-06-27

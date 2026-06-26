# MediaPrepTool

## Purpose

MediaPrepTool provides cross-platform media quality control for live events, LED playback, launch events, Millumin, Disguise, Pixera, TouchDesigner, and Notch workflows.

## Overview

The CLI package is currently exposed as `mediaqc`. It scans media folders, hashes files, probes technical metadata with FFmpeg tools, validates project rules and profiles, generates reports, tracks scan state in SQLite, watches folders for live updates, and serves a dashboard.

## Architecture

- `mediaqc/cli.py`: Typer command surface.
- `mediaqc/scanner.py`: Recursive media discovery.
- `mediaqc/probe.py`: `ffprobe` metadata extraction.
- `mediaqc/deep_analysis.py`: FFmpeg decode and frame-level analysis.
- `mediaqc/validation_engine.py` and `mediaqc/validators/`: Modular validation engine.
- `mediaqc/live_event/`: Live event output, canvas, codec risk, manifest, and integrity extensions.
- `mediaqc/database.py`: SQLite persistence and hash cache.
- `mediaqc/dashboard.py`: FastAPI dashboard and REST API.

## Workflow

Install dependencies, scan a media folder, review reports, then optionally open the dashboard:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .

mediaqc scan ./Media --profile disguise --output ./reports --html
mediaqc dashboard --database ./reports/media.db
```

Live event workflow:

```bash
mediaqc scan ./Media \
  --rules ./config/project_rules.yaml \
  --output-spec ./config/output_spec.yaml \
  --canvas-spec ./config/canvas_spec.yaml \
  --output ./reports \
  --html \
  --manifest
```

## Dependencies

- Python 3.11+
- FFmpeg command-line tools: `ffmpeg`, `ffprobe`
- Python packages from `requirements.txt`

## Configuration

Project rules and live event specs are YAML files:

- `project_rules.yaml`
- `config/project_rules.yaml`
- `config/output_spec.yaml`
- `config/canvas_spec.yaml`
- `profiles/*.yaml`

## Example

```bash
mediaqc manifest ./Media --output ./reports
mediaqc verify ./Media --manifest ./reports/manifest.json
mediaqc duplicates --database ./reports/media.db
```

## Known Limitations

- EDID support currently validates project output specs, not real GPU EDID data.
- Dashboard assets use CDN-hosted Bootstrap, HTMX, and Chart.js.
- The package name is `mediaqc`; repository-level documentation uses the product name MediaPrepTool.

## Future Improvements

- Real EDID acquisition.
- Vue dashboard using the existing REST API.
- Dedicated plugin SDK examples.
- Additional codec-specific playback heuristics.

## Related Modules

- `mediaqc/live_event/edid.py`
- `mediaqc/live_event/canvas.py`
- `mediaqc/live_event/codec_profiles.py`
- `mediaqc/live_event/manifest.py`
- `mediaqc/live_event/integrity.py`

## Revision History

- Documentation version: 0.95
- Last updated: 2026-06-26

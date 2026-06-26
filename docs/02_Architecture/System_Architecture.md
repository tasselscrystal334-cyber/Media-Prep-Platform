# System Architecture

## Purpose

Describe the current MediaPrepTool system architecture.

## Overview

MediaPrepTool is a Python application with a Typer CLI, modular validation engine, live event extensions, SQLite persistence, generated reports, and a FastAPI dashboard.

## Architecture

- CLI: `mediaqc/cli.py`
- Scanner: `mediaqc/scanner.py`
- Hashing: `mediaqc/hash_check.py`
- Metadata probing: `mediaqc/probe.py`
- Deep analysis: `mediaqc/deep_analysis.py`
- Validation engine: `mediaqc/validation_engine.py`
- Validators: `mediaqc/validators/`
- Live event extension: `mediaqc/live_event/`
- Reports: `mediaqc/report.py`, `mediaqc/templates/`
- Dashboard: `mediaqc/dashboard.py`, `mediaqc/dashboard_templates/`
- Database: `mediaqc/database.py`

## Workflow

1. Scan files.
2. Calculate or reuse SHA256 from `HashCache`.
3. Probe metadata with `ffprobe`.
4. Run validators and optional live event checks.
5. Persist results in SQLite.
6. Write JSON, CSV, HTML, and optional manifest outputs.

## Dependencies

- Python 3.11+
- FFmpeg tools
- Typer
- Rich
- PyYAML
- Jinja2
- Watchdog
- FastAPI
- Uvicorn

## Configuration

YAML files configure rules, profiles, output specs, and canvas specs.

## Example

```bash
mediaqc scan ./Media --profile disguise --output ./reports --html
```

## Known Limitations

Source code currently lives in `mediaqc/`; the repository target structure reserves `src/` for future packaging migration.

## Future Improvements

- Move package source under `src/` during packaging hardening.
- Add plugin documentation and examples.

## Related Modules

- `mediaqc/cli.py`
- `mediaqc/validation_engine.py`
- `mediaqc/live_event/`

## Revision History

- Documentation version: 0.95

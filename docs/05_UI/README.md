# README

## Purpose

Document the README responsibilities in the 05_UI documentation area.

## Overview

Covers the V1.0 PySide6 studio UI with a soft light professional batch media workspace, media import toolbar, output settings, source/output preview pages, logs, settings, themes, and shortcuts.

## Architecture

The GUI lives under `mediaqc/gui/`. PySide6 imports are delayed until `mediaqc gui` starts so CLI and test environments do not require GUI dependencies. Scanning is executed in a background thread and reuses existing report writers.

## Workflow

Launch with `mediaqc gui`. Operators can drop folders or files, queue multiple projects, start scans, request cancellation, watch progress, inspect logs, and open generated HTML/PDF reports.

## Dependencies

Python 3.11+, optional `PySide6`, FFmpeg tooling, SQLite, Jinja2, PyYAML, and the existing scan/report stack.

## Configuration

GUI scans currently use explicit folder/output selection and existing YAML/project profile files. Future settings should remain versionable and documented.

## Example

```bash
python -m pip install "mediaqc[gui]"
mediaqc gui
```

## Known Limitations

Cancellation is cooperative. If a scan is already inside a long file operation, the current operation may finish before the UI marks the job cancelled.

## Future Improvements

Add persistent GUI settings, richer preview playback, PDF styling, rule/profile editing, and dashboard handoff.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/gui/main_window.py`
- `mediaqc/gui/workers.py`
- `mediaqc/report.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-29

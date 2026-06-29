# Workspace

## Purpose

Document the Workspace responsibilities in the 05_UI documentation area.

## Overview

Covers the V1.0 workspace layout: left Projects/Rules/History navigation, center Scan workspace, and right Preview/Logs panel.

## Architecture

`MainWindow` composes the workspace with Qt splitters and tabs. Scan execution is delegated to `ScanWorker` and `QtScanThread` so the UI remains responsive.

## Workflow

Operators drag folders or files into the scan field, build a project queue, start scans, request cancellation, and inspect generated outputs.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

The workspace exports JSON, CSV, HTML, and PDF into the selected output folder for each queued project.

## Known Limitations

The V1.0 workspace is focused on scanning and reporting. Editing rules inside the GUI is reserved for a later milestone.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/gui/main_window.py`
- `mediaqc/gui/queue.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-29

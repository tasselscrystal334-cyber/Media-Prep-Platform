# Workspace

## Purpose

Document the Workspace responsibilities in the 05_UI documentation area.

## Overview

Covers the V1.0 workspace layout: in-window Loom menu bar, top source/action toolbar, source title dropdown, scan range, grouped preset menu, output format selector, parameter tabs, scan queue, and right Source Preview / Output Preview comparison panel.

## Architecture

`MainWindow` composes the workspace with source controls, Qt splitters, tabs, and queue tables. Scan execution is delegated to `ScanWorker` and `QtScanThread` so the UI remains responsive. Source preview filtering is delegated to `mediaqc/gui/source_preview.py`.

## Workflow

Operators drag folders or files into the source field, choose a title from the detected media dropdown, choose a scan range, choose a grouped preset, choose an output format, build a project queue, start scans, request cancellation, open Activity logs from the toolbar, and inspect generated outputs.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

The workspace exports JSON, CSV, HTML, and PDF into the selected output folder for each queued project. Source preview lists show only supported top-level media files and exclude `.DS_Store`, folders, and unsupported sidecar files. Start Live Preview updates the output preview summary and preview frame for the selected title, preset, format, duration, and output name.

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
- `mediaqc/gui/source_preview.py`

## Revision History

- Documentation version: 1.4
- Last updated: 2026-06-29

# PreviewWindow

## Purpose

Document the PreviewWindow responsibilities in the 05_UI documentation area.

## Overview

Covers the right-side Preview and Logs tabs in the V1.0 PySide6 GUI.

## Architecture

The preview pane shows generated report output paths and can open HTML/PDF reports through desktop services. The log pane records scan lifecycle events and cancellation requests.

## Workflow

Before changing related code, read this document and nearby architecture notes. After implementation, update this document, tests, examples, and changelog entries where needed.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

After a scan, use Open HTML or the File menu Export PDF action to inspect generated reports.

## Known Limitations

This is not a video playback surface yet. FFplay preview remains available through `mediaqc play`.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/gui/main_window.py`
- `mediaqc/processing/ffplay.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

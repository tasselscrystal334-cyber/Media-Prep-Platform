# Workspace

## Purpose

Document the Workspace responsibilities in the 05_UI documentation area.

## Overview

Covers the V1.0 workspace layout: in-window Loom menu bar, top action toolbar, media import list, output setting controls, destination and renaming controls, output file table, and paged right-side Source Preview, Output Preview, and Logs panels.

## Architecture

`MainWindow` composes the workspace with a single Import entry, drag-and-drop media intake, scrollable Qt splitters, output planning tables, preview tabs, FFplay control dialogs, and background worker threads. Scan execution is delegated to `ScanWorker` and `QtScanThread`; transcode execution is delegated to a GUI `TranscodeThread`. Source preview filtering is delegated to `mediaqc/gui/source_preview.py`.

## Workflow

Operators import files or drag media folders into the Files to process list. They choose Codec, Frame Rate, Proxy, Format, destination, and renaming options, then run Analyze, SHA256, Play, or Transcode. Rules are customized in YAML under `config/` and do not occupy the main workspace.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

The workspace exports JSON, CSV, HTML, and PDF for analysis/reporting and writes transcoded files to the source folder by default. Operators can choose a custom destination and batch rename with remove, append, and prefix controls. Format defaults to MOV; audio defaults to Copy original audio. Start Live Preview generates a short output preview video for the selected file, settings, duration, and output name, then launches FFplay for realtime playback with Loom Player Controls.

## Known Limitations

Embedded video playback is not yet inside the Qt panel; playback and live previews launch FFplay in separate windows.

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

- Documentation version: 1.5
- Last updated: 2026-06-30

# PreviewWindow

## Purpose

Document the PreviewWindow responsibilities in the 05_UI documentation area.

## Overview

Covers the paged right-side Source Preview, Output Preview, and Logs surfaces in the V1.0 PySide6 GUI.

## Architecture

The Source Preview page lists the selected source file and path. The Output Preview page shows generated report output paths, live preview summaries, crop controls, generated preview video paths, and realtime FFplay playback status. Fixed preview panel heights prevent Start Live Preview from resizing the workspace. The Logs page records scan, playback, transcode, and cancellation events.

## Workflow

Before changing related code, read this document and nearby architecture notes. After implementation, update this document, tests, examples, and changelog entries where needed.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

After a scan, use Open HTML or the File menu Export PDF action to inspect generated reports. For output preview, choose a file, codec, frame rate, proxy, format, and preview duration, then click Start Live Preview to generate a short output preview video and play the whole segment in FFplay. Play opens the selected source in a separate fullscreen FFplay window.

## Known Limitations

The current desktop preview launches FFplay as a separate playback window rather than embedding video playback directly inside the Qt panel.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/gui/main_window.py`
- `mediaqc/gui/source_preview.py`
- `mediaqc/processing/ffplay.py`

## Revision History

- Documentation version: 1.6
- Last updated: 2026-06-29

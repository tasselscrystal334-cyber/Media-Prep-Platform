# Toolbar

## Purpose

Document the Toolbar responsibilities in the 05_UI documentation area.

## Overview

Covers the top source/action toolbar in the Loom desktop GUI.

## Architecture

`MainWindow` builds a light, HandBrake-style toolbar above the source controls. Primary actions include Open Source, Add Queue, Start, and Pause. Activity focuses the logs tab. Project presets are selected from the source control row rather than duplicated in the toolbar.

## Workflow

Operators choose a source, optionally add it to the queue, start scanning, pause/cancel when needed, and use Activity to inspect logs.

## Dependencies

Python 3.11+ and PySide6.

## Configuration

The source-row preset selector mirrors the built-in project profiles and remains backed by YAML profile files.

## Example

Run `loom-gui`, open a source folder, choose a source-row preset, start a scan, and click Activity to focus logs.

## Known Limitations

Toolbar actions are currently text buttons. Native icon assets can be added later once the design system is stable.

## Future Improvements

Add icons, keyboard shortcuts, and persistent toolbar state.

## Related Modules

- `README.md`
- `docs/04_UI/DesktopGUI.md`
- `mediaqc/gui/main_window.py`
- `mediaqc/gui/theme.py`

## Revision History

- Documentation version: 1.2
- Last updated: 2026-06-29

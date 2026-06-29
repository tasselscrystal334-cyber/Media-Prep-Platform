# Toolbar

## Purpose

Document the Toolbar responsibilities in the 05_UI documentation area.

## Overview

Covers the top source/action toolbar in the Loom desktop GUI.

## Architecture

`MainWindow` builds a light, HandBrake-style toolbar above the source controls. Primary actions include Open Source, Add Queue, Start, and Pause. Secondary actions include Presets, Preview, Queue, and Activity. Presets opens a profile menu; Preview focuses the source/output comparison tab; Queue focuses the task queue; Activity focuses the logs tab.

## Workflow

Operators choose a source, optionally add it to the queue, start scanning, and use Preview/Queue/Activity to move through the active workspace areas.

## Dependencies

Python 3.11+ and PySide6.

## Configuration

Toolbar preset names mirror the built-in project profiles and remain backed by YAML profile files.

## Example

Run `loom-gui`, open a source folder, click Presets to verify the profile menu, click Preview to focus comparison panes, and click Activity to focus logs.

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

- Documentation version: 1.1
- Last updated: 2026-06-29

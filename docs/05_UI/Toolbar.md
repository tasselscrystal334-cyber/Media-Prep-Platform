# Toolbar

## Purpose

Document the Toolbar responsibilities in the 05_UI documentation area.

## Overview

Covers the top source/action toolbar in the Loom desktop GUI.

## Architecture

`MainWindow` builds a light batch media toolbar above the workspace. Primary actions include Import, Analyze, SHA256, Play, and Transcode. Activity focuses the logs tab. Encoding, frame-rate, proxy, and format choices live in the output settings column.

## Workflow

Operators use the single Import action for one or more files, or drag files/folders into the file list, then run analysis, SHA256 verification, playback, or transcode/export directly from the file list. Activity opens operational logs.

## Dependencies

Python 3.11+ and PySide6.

## Configuration

The source-row preset selector mirrors the built-in project profiles and remains backed by YAML profile files.

## Example

Run `loom-gui`, import media, choose output settings, start analysis or transcode, and click Activity to focus logs.

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

- Documentation version: 1.3
- Last updated: 2026-06-30

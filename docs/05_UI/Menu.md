# Menu

## Purpose

Document the Menu responsibilities in the 05_UI documentation area.

## Overview

Covers the Loom desktop GUI menu system for local Python launches and packaged app runs.

## Architecture

`MainWindow` creates an in-window Qt menu bar instead of relying on the native macOS menu bar during local Python launches. This keeps the visible application menu branded as Loom even when the process is started by the Python interpreter. Menus expose Loom, File, Edit, View, Presets, Window, and Help actions.

## Workflow

Operators use File for project/report actions, Edit for queue clearing, View for Welcome/Workspace switching, Presets for profile selection, Window for standard window actions, and Help for diagnostics hints.

## Dependencies

Python 3.11+ and PySide6.

## Configuration

Menu actions use the same local profile and report state as the main window. Persistent menu customization is not implemented.

## Example

Run `loom-gui` locally. The visible window menu should start with Loom rather than Python.

## Known Limitations

The local Python process can still appear as Python in platform-level process listings. The visible application menu inside the Loom window is the supported local development surface.

## Future Improvements

Add persistent recent-project menu entries and a GUI Tools Doctor panel.

## Related Modules

- `README.md`
- `docs/04_UI/DesktopGUI.md`
- `mediaqc/gui/main_window.py`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-29

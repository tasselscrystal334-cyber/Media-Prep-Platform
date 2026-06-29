# Local Deployment

## Purpose

Document local installation and runtime.

## Overview

Loom can run as a local Python CLI, PySide6 desktop GUI, and FastAPI service. For active development, the local repository is the primary preview surface. GitHub is used for remote backup and releases, not as the place operators should repeatedly download day-to-day changes from.

## Architecture

The local environment uses a Python virtual environment and installed console script.

## Workflow

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

For live local refreshes from the current working tree:

```bash
scripts/local_live_update.sh
scripts/local_live_update.sh --launch
scripts/local_live_update.sh --install-tools --launch
scripts/install_loom_local_app.sh
```

The live update script creates or reuses `.venv`, installs Loom with `pip install -e ".[gui,dev]"`, runs tests by default, reports FFmpeg-family tool paths through `mediaqc tools doctor`, and optionally launches the GUI. On macOS, launch uses `scripts/launch_loom_macos.sh` to generate `.local_app/Loom.app` and open the GUI through that local app wrapper. `scripts/install_loom_local_app.sh` installs `/Applications/Loom Local.app`, a development launcher that always points to this working tree. Quit older packaged or Python-launched GUI windows before testing the local launcher. This keeps local validation tied to the files on disk and avoids downloading release assets for every development change.

## Dependencies

- Python 3.11+
- FFmpeg tools with automatic install support
- Optional PySide6 for the local desktop GUI

## Configuration

Runtime configuration is passed through CLI options and YAML files.

## Example

```bash
mediaqc dashboard --database ./reports/media.db --host 127.0.0.1 --port 8000
```

```bash
scripts/local_live_update.sh --launch
```

## Known Limitations

Packaged desktop builds depend on platform security settings, code signing, and FFmpeg tool availability.
Editable local installs reflect Python source changes immediately, but packaged `.pkg` or `.app` builds still require a rebuild when validating installer behavior.
The generated `.local_app/Loom.app` is a development launcher and is ignored by Git.
`/Applications/Loom Local.app` is also a development launcher; reinstall it after moving the repository.

## Future Improvements

Add signed platform installers.
Add a GUI-accessible development update action when the desktop settings model becomes persistent.

## Related Modules

- `pyproject.toml`
- `requirements.txt`
- `scripts/local_live_update.sh`
- `scripts/launch_loom_macos.sh`
- `scripts/install_loom_local_app.sh`

## Revision History

- Documentation version: 1.3
- Last updated: 2026-06-30

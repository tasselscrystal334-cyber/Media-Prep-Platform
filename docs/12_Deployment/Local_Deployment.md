# Local Deployment

## Purpose

Document local installation and runtime.

## Overview

Loom can run as a local Python CLI, PySide6 desktop GUI, and FastAPI service.

## Architecture

The local environment uses a Python virtual environment and installed console script.

## Workflow

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Dependencies

- Python 3.11+
- FFmpeg tools with automatic install support

## Configuration

Runtime configuration is passed through CLI options and YAML files.

## Example

```bash
mediaqc dashboard --database ./reports/media.db --host 127.0.0.1 --port 8000
```

## Known Limitations

Packaged desktop builds depend on platform security settings, code signing, and FFmpeg tool availability.

## Future Improvements

Add signed platform installers.

## Related Modules

- `pyproject.toml`
- `requirements.txt`

## Revision History

- Documentation version: 0.95

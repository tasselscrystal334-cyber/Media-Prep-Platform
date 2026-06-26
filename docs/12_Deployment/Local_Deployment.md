# Local Deployment

## Purpose

Document local installation and runtime.

## Overview

MediaPrepTool is currently deployed as a local Python CLI and FastAPI service.

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
- FFmpeg tools

## Configuration

Runtime configuration is passed through CLI options and YAML files.

## Example

```bash
mediaqc dashboard --database ./reports/media.db --host 127.0.0.1 --port 8000
```

## Known Limitations

No packaged binary or desktop app exists yet.

## Future Improvements

Add packaged installers.

## Related Modules

- `pyproject.toml`
- `requirements.txt`

## Revision History

- Documentation version: 0.95

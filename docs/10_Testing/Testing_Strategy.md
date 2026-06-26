# Testing Strategy

## Purpose

Describe project test expectations.

## Overview

Tests cover scanner, hashing, validators, database, dashboard, deep analysis, live event canvas, manifest, and integrity workflows.

## Architecture

Tests live in `tests/` and use `pytest`.

## Workflow

```bash
python -m pytest
```

## Dependencies

- pytest
- FastAPI TestClient dependencies

## Configuration

No special test configuration is required.

## Example

```bash
.venv/bin/python -m pytest tests/test_manifest.py
```

## Known Limitations

Most tests avoid real video files and rely on synthetic metadata.

## Future Improvements

Add fixture media samples and integration tests for real FFmpeg output.

## Related Modules

- `tests/`

## Revision History

- Documentation version: 0.95

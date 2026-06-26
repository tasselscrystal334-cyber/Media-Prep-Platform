# REST API

## Purpose

Document the dashboard REST API.

## Overview

The FastAPI dashboard exposes JSON endpoints for future Vue or other frontends.

## Architecture

REST routes are implemented in `mediaqc/dashboard.py`.

## Workflow

Run:

```bash
mediaqc dashboard --database ./reports/media.db
```

## Dependencies

- FastAPI
- Uvicorn

## Configuration

Use `--database`, `--host`, and `--port`.

## Example

```text
GET /api/overview
GET /api/projects
GET /api/history
GET /api/files
GET /api/search?q=Opening
GET /api/statistics
GET /api/duplicates
```

## Known Limitations

No authentication is implemented.

## Future Improvements

Add API versioning and optional authentication.

## Related Modules

- `mediaqc/dashboard.py`

## Revision History

- Documentation version: 0.95

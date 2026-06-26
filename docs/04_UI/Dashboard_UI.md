# Dashboard UI

## Purpose

Document the current dashboard user interface.

## Overview

The dashboard is a FastAPI server-rendered interface using HTMX, Bootstrap, and Chart.js.

## Architecture

Templates live in `mediaqc/dashboard_templates/`.

## Workflow

```bash
mediaqc dashboard --database ./reports/media.db
```

## Dependencies

- FastAPI
- Jinja2
- HTMX CDN
- Bootstrap CDN
- Chart.js CDN

## Configuration

Use `--host`, `--port`, and `--database`.

## Example

Open `http://127.0.0.1:8000`.

## Known Limitations

The UI currently depends on CDN-hosted frontend libraries.

## Future Improvements

Add a Vue frontend using the existing REST API.

## Related Modules

- `mediaqc/dashboard.py`
- `mediaqc/dashboard_templates/`

## Revision History

- Documentation version: 0.95

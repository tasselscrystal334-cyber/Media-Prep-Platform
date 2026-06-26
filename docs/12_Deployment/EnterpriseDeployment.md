# EnterpriseDeployment

## Purpose

Document the EnterpriseDeployment responsibilities in the 12_Deployment documentation area.

## Overview

Covers packaging, installers, auto update, enterprise deployment, Windows, macOS, Linux, portable mode, offline install, and V2.0 container deployment.

## Architecture

V2.0 deployment uses Docker Compose for local enterprise stacks: API, PostgreSQL, Redis, RabbitMQ, MinIO, and optional Celery worker.

## Workflow

Before changing related code, read this document and nearby architecture notes. After implementation, update this document, tests, examples, and changelog entries where needed.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

```bash
cp .env.example .env
docker compose up
```

## Known Limitations

The Compose stack is a development/reference deployment. Production deployments require secrets management, TLS, backups, monitoring, and external identity providers.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `docker-compose.yml`
- `Dockerfile`
- `.env.example`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

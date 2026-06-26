# Enterprise MAM Architecture

## Purpose

Document the V2.0 Media Asset Management architecture for enterprise deployment.

## Overview

V2.0 introduces users, permissions, project management, enterprise dashboard overview, REST API, GraphQL, webhooks, notifications, and storage adapters for NAS, S3, Azure, Google Drive, and WebDAV.

## Architecture

The enterprise layer lives under `mediaqc/enterprise/` and is intentionally separated from the existing CLI scan pipeline. The default implementation uses in-memory repositories for local development and tests. Production deployment is expected to use PostgreSQL, Redis, Celery, RabbitMQ, and MinIO or external object storage.

## Workflow

Operators and integrations create users, create projects, attach assets, trigger pipeline jobs, subscribe to webhooks, and receive notifications through Slack, Teams, Feishu, or email.

## Dependencies

- FastAPI for REST and OpenAPI.
- Optional PostgreSQL for durable metadata.
- Optional Redis, RabbitMQ, and Celery for async work.
- Optional MinIO/S3/Azure/Google Drive/WebDAV storage backends.

## Configuration

Configuration is read from environment variables and `.env.example`. Docker Compose provides local service wiring.

## Example

```bash
mediaqc enterprise-api --host 0.0.0.0 --port 8080
docker compose up
```

## Known Limitations

The V2.0 code path provides a working API foundation and adapter contracts. Production-grade OAuth/SSO, persistent migrations, and background workers are staged for later hardening.

## Future Improvements

Add SQLAlchemy repositories, Alembic migrations, SSO, audit logs, persistent Celery workers, and cloud storage SDK implementations.

## Related Modules

- `mediaqc/enterprise/api.py`
- `mediaqc/enterprise/auth.py`
- `mediaqc/enterprise/storage.py`
- `mediaqc/enterprise/notifications.py`

## Revision History

- Documentation version: 2.0
- Last updated: 2026-06-27

# REST API

## Purpose

Document the RESTAPI responsibilities in the 10_API documentation area.

## Overview

Covers application, project, asset, codec, validation, Python, CLI, plugin, and enterprise REST APIs. V2.0 adds an enterprise FastAPI app with OpenAPI, dashboard overview, users, permissions, projects, assets, webhooks, notifications, and GraphQL entry points.

## Architecture

This area must respect the layered architecture, avoid circular dependencies, and keep feature-specific behavior behind documented service, plugin, API, or configuration boundaries.

## Workflow

Before changing related code, read this document and nearby architecture notes. After implementation, update this document, tests, examples, and changelog entries where needed.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

Use this document as the reference when implementing or reviewing RESTAPI changes.

## Known Limitations

Authentication is token-based in the V2.0 foundation and intended for replacement with enterprise SSO/OAuth in later releases. Persistent PostgreSQL repositories are planned after the in-memory reference implementation.

## Future Improvements

Add versioned API schemas, pagination standards, OAuth scopes, webhook signatures, and OpenAPI release governance.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/enterprise/api.py`
- `mediaqc/enterprise/graphql.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

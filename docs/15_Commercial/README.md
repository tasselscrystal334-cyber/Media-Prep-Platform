# README

## Purpose

Define the commercial documentation area for MediaPrep Studio Enterprise Edition.

## Overview

Covers commercial licensing, offline activation, enterprise deployment, crash reporting, auto update, plugin marketplace, license server, pricing, commercial roadmap, and the Enterprise Edition feature boundary.

Community Edition is licensed under Apache License 2.0. Enterprise Edition is licensed under a commercial license and covers multi-user permissions, LDAP/AD, audit logs, NAS cluster workflows, the web management dashboard, automatic content distribution, and Render Farm management.

## Architecture

This area must respect the layered architecture, avoid circular dependencies, and keep feature-specific behavior behind documented service, plugin, API, or configuration boundaries.

## Workflow

Before changing related code, read this document and nearby architecture notes. After implementation, update this document, tests, examples, and changelog entries where needed.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

Use `mediaqc editions` and `docs/00_Project/Editions.md` as the first reference when implementing or reviewing edition-specific behavior.

## Known Limitations

This document describes the intended architecture and current command-line implementation. Desktop, cloud, and enterprise features may be staged behind roadmap milestones.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/00_Project/Editions.md`
- `docs/01_Architecture/SystemOverview.md`
- `docs/15_Commercial/Licensing.md`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-27

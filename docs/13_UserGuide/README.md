# README

## Purpose

Document the README responsibilities in the 13_UserGuide documentation area.

## Overview

Covers installation, quick start, projects, assets, validation, preview, encoding, batch processing, export, reports, settings, plugins, troubleshooting, and FAQ.

## Architecture

This area must respect the layered architecture, avoid circular dependencies, and keep feature-specific behavior behind documented service, plugin, API, or configuration boundaries.

## Workflow

Before changing related code, read this document and nearby architecture notes. After implementation, update this document, tests, examples, and changelog entries where needed.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for future desktop UI, and platform GPU APIs when applicable.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

Use this document as the reference when implementing or reviewing README changes.

## Known Limitations

This document describes the intended architecture and current command-line implementation. Desktop, cloud, and enterprise features may be staged behind roadmap milestones.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

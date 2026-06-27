# README

## Purpose

Document the README responsibilities in the 04_Pipeline documentation area.

## Overview

Covers import, discovery, metadata, hash, validation, quality control, preview, processing, verification, NAS/server synchronization, packaging, and export.

## Architecture

This area must respect the layered architecture, avoid circular dependencies, and keep feature-specific behavior behind documented service, plugin, API, or configuration boundaries. V1.5 adds `mediaqc/pipeline/` for NAS-mounted sync, metadata enrichment, SHA256 comparison, transfer reporting, and project package generation.

## Workflow

Before changing related code, read this document and nearby architecture notes. After implementation, update this document, tests, examples, and changelog entries where needed. Pipeline commands should continue after per-file failures and produce JSON/CSV audit reports.

## Dependencies

Relevant dependencies may include Python 3.11+, FFmpeg tooling, optional MediaInfo CLI, SQLite, FastAPI, Typer, Rich, Jinja2, PyYAML, watchdog, PySide6 for desktop UI, and platform filesystem mounts for SMB/AFP/NFS.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, package metadata, and future project settings unless an architecture document approves another format.

## Example

```bash
mediaqc pipeline sync ./Media --destination /Volumes/ShowNAS/Media --profile disguise --output ./reports
mediaqc pipeline compare ./Media --destination /Volumes/ShowNAS/Media --output ./reports
mediaqc pipeline package ./Media --profile notch --output ./packages
```

## Known Limitations

SMB, AFP, and NFS are handled as mounted paths. Loom does not mount remote shares itself in V1.5.

## Future Improvements

Add native mount helpers, resumable remote transfer sessions, conflict policy configuration, and distributed processing workers.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/pipeline/sync.py`
- `mediaqc/pipeline/package.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

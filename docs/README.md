# MediaPrep Studio Documentation

## Purpose

Provide the central index for repository documentation.

## Overview

Documentation is organized by project, architecture, development, codecs, pipeline, UI, render, GPU, database, plugins, API, testing, deployment, user guide, AI collaboration, commercial planning, operations, and specifications.

## Architecture

This document aligns with the MediaPrep Studio layered architecture: presentation, application, services, core, infrastructure, codec engine, media engine, and hardware integration.

## Workflow

Read this document before changing related code, update implementation and tests, then revise documentation if behavior changes.

## Dependencies

Python 3.11+, FFmpeg tools where media probing or processing is involved, and the project dependencies declared in `requirements.txt` and `pyproject.toml`.

## Configuration

Configuration is stored in YAML project rules, profiles, output specifications, canvas specifications, and future application settings.

## Example

Open this file in Typora with `open -a Typora docs/README.md` on macOS or `Start-Process "typora" "docs/README.md"` in Windows PowerShell.

## Known Limitations

This document describes the intended architecture and current command-line implementation. Desktop, cloud, and enterprise features may be staged behind roadmap milestones.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `PROJECT_CONSTITUTION.md`
- `docs/00_Project/README.md`
- `docs/17_Specifications/README.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

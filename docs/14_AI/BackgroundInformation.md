# Background Information

## Purpose

Provide a compact context block that can be placed into Codex Background Information.

## Overview

MediaPrep Studio is a professional media preparation and QC platform for live events, XR, broadcast, exhibitions, digital venues, and media-server workflows. The current Python package is `mediaqc` and uses Typer, Rich, FFmpeg/FFprobe, SQLite, YAML, Jinja2, watchdog, FastAPI, and pytest.

## Architecture

Architecture rules: respect layered ownership, use `pathlib.Path`, avoid `shell=True`, keep validators modular, avoid duplicate modules, document new subsystems before implementation, and prefer existing service boundaries.

## Workflow

AI development workflow: read relevant docs, design, update documentation, implement, add or update tests, update docs again, then commit. Do not treat chat history as permanent documentation.

## Dependencies

Python 3.11+, FFmpeg tools where media probing or processing is involved, and the project dependencies declared in `requirements.txt` and `pyproject.toml`.

## Configuration

Documentation rules: all durable decisions live in GitHub Markdown. Every new API, module, plugin, configuration, codec, pipeline, UI, database, deployment, or test workflow change must update docs and tests.

## Example

Instruction summary for AI contributors: do not duplicate modules, do not overwrite user work, keep generated reports and databases out of Git, always update docs and tests.

## Known Limitations

This document describes the intended architecture and current command-line implementation. Desktop, cloud, and enterprise features may be staged behind roadmap milestones.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `PROJECT_CONSTITUTION.md`
- `CONTRIBUTING.md`
- `docs/14_AI/AIDocumentationPolicy.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

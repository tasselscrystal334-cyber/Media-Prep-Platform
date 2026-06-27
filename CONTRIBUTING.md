# Contributing

## Purpose

Define how humans and AI contributors safely change Loom.

## Overview

Every change must preserve architecture, tests, and documentation. The GitHub repository is the source of truth for standards and decisions.

## Architecture

This document aligns with the Loom layered architecture: presentation, application, services, core, infrastructure, codec engine, media engine, and hardware integration.

## Workflow

Use Git Flow-style branches: `feature/<topic>`, `fix/<topic>`, `docs/<topic>`, `test/<topic>`, and `release/<version>`. Commit messages should follow Conventional Commits such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, and `chore:`. Pull requests must include scope, test evidence, documentation updates, and risk notes.

## Dependencies

Python 3.11+, FFmpeg tools where media probing or processing is involved, and the project dependencies declared in `requirements.txt` and `pyproject.toml`.

## Configuration

Configuration is stored in YAML project rules, profiles, output specifications, canvas specifications, and future application settings.

## Example

Definition of Done: design documented, code implemented, tests passing, docs updated, changelog updated when user-facing behavior changes, and review checklist complete.

## Known Limitations

This document describes the intended architecture and current command-line implementation. Desktop, cloud, and enterprise features may be staged behind roadmap milestones.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `PROJECT_CONSTITUTION.md`
- `docs/02_Development/GitWorkflow.md`
- `docs/02_Development/DefinitionOfDone.md`
- `docs/14_AI/AICommitRules.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

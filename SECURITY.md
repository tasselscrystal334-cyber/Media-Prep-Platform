# Security Policy

## Purpose

Define how security issues, dependency risks, media-file risks, and disclosure are handled.

## Overview

Loom processes untrusted media files and project archives. Contributors must treat parsing, probing, preview, and plugin execution as security-sensitive surfaces.

## Architecture

This document aligns with the Loom layered architecture: presentation, application, services, core, infrastructure, codec engine, media engine, and hardware integration.

## Workflow

Report vulnerabilities privately through the repository security channel when available. Do not publish exploit details before a fix and release note are prepared.

## Dependencies

Python 3.11+, FFmpeg tools where media probing or processing is involved, and the project dependencies declared in `requirements.txt` and `pyproject.toml`.

## Configuration

Never commit production secrets, license keys, activation tokens, customer media, private manifests, or generated databases.

## Example

Use `subprocess` without `shell=True` for FFmpeg tools and validate paths with `pathlib.Path`.

## Known Limitations

This document describes the intended architecture and current command-line implementation. Desktop, cloud, and enterprise features may be staged behind roadmap milestones.

## Future Improvements

Expand this document when the subsystem receives a new module, public API, UI surface, or deployment contract.

## Related Modules

- `docs/01_Architecture/ErrorHandling.md`
- `docs/09_Plugins/PluginPermissions.md`
- `docs/12_Deployment/EnterpriseDeployment.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

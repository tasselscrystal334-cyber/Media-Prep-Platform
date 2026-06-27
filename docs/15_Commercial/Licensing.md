# Licensing

## Purpose

Document MediaPrep Studio licensing boundaries for Community Edition and Enterprise Edition.

## Overview

MediaPrep Studio Community Edition is licensed under Apache License 2.0. Community Edition includes:

- FFmpeg integration
- FFprobe metadata extraction
- SHA256 verification
- Media validation
- Batch transcoding

MediaPrep Studio Enterprise Edition is licensed under a commercial license. Enterprise Edition includes:

- Multi-user permissions
- LDAP/AD integration
- Audit logs
- NAS cluster workflows
- Web management dashboard
- Automatic content distribution
- Render Farm management

## Architecture

The source-of-truth edition matrix lives in `mediaqc/editions.py` and is exposed through `mediaqc editions`. Community Edition functionality should remain usable through local CLI, GUI, and project workflows. Enterprise Edition functionality should remain documented as commercial behavior in architecture, deployment, API, and operations documents.

## Workflow

When a feature is added, classify it before implementation:

1. Community Edition when it supports local media preparation, FFmpeg/FFprobe analysis, checksums, validation, or batch transcode workflows.
2. Enterprise Edition when it adds organization identity, access control, auditability, clustered infrastructure, managed distribution, render farm orchestration, or enterprise web administration.

After implementation, update README, this document, `docs/00_Project/Editions.md`, tests, changelog entries, and any affected API or deployment documents.

## Dependencies

Community Edition depends on Python 3.11+, FFmpeg/FFprobe, Typer, Rich, SQLite, YAML configuration, and local reporting dependencies.

Enterprise Edition may depend on FastAPI, PostgreSQL, Redis, Celery, RabbitMQ, MinIO, LDAP/AD, NAS cluster infrastructure, webhook/notification providers, and commercial license activation services.

## Configuration

Community Edition configuration is file-based and project-local: rules, profiles, transcode presets, output specs, canvas specs, and report folders.

Enterprise Edition configuration may include deployment environment variables, identity provider settings, storage backends, audit retention, content distribution targets, render farm nodes, and commercial license activation.

## Example

```bash
mediaqc editions
```

Expected edition boundaries:

- Community Edition: Apache License 2.0.
- Enterprise Edition: Commercial License.

## Known Limitations

Enterprise foundation modules exist in this repository for development and evaluation, but production Enterprise Edition use requires a commercial license. Runtime feature gating and license activation are not yet enforced in the current `1.0.0` release line.

## Future Improvements

- Add runtime commercial license activation for enterprise services.
- Add explicit enterprise feature gates to commercial-only commands.
- Generate edition-specific release notes and binary distribution metadata.

## Related Modules

- `mediaqc/editions.py`
- `mediaqc/cli.py`
- `mediaqc/enterprise/`
- `docs/00_Project/Editions.md`
- `docs/12_Deployment/EnterpriseDeployment.md`
- `README.md`

## Revision History

- Documentation version: 1.1
- Last updated: 2026-06-27

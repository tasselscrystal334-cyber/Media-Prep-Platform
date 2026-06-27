# Product Editions

## Purpose

Define the supported Loom product editions, licensing boundaries, and capability ownership for the current `1.0.0` release line.

## Overview

Loom uses a dual-edition model.

Community Edition is licensed under Apache License 2.0. It provides the operator-facing media preparation features needed for local and project-based workflows:

- FFmpeg integration
- FFprobe metadata extraction
- SHA256 verification
- Media validation
- Batch transcoding

Enterprise Edition is licensed under a commercial license. It provides organization-scale workflow, governance, and distribution features:

- Multi-user permissions
- LDAP/AD integration
- Audit logs
- NAS cluster workflows
- Web management dashboard
- Automatic content distribution
- Render Farm management

## Architecture

The edition metadata is implemented in `mediaqc/editions.py` and displayed by the `mediaqc editions` CLI command. Community features remain available through the normal CLI and local workflows. Enterprise capabilities are implemented under documented commercial modules and should remain explicitly marked as Enterprise Edition behavior in user-facing documentation.

## Workflow

Use `mediaqc editions` to inspect the current edition matrix. When adding a capability, first decide whether it belongs to Community Edition or Enterprise Edition, then update this document, `docs/15_Commercial/Licensing.md`, README references, changelog entries, and tests.

## Dependencies

Community Edition depends on Python 3.11+, FFmpeg tooling, FFprobe, Typer, Rich, SQLite, YAML configuration, and the processing/reporting dependencies documented in the main README.

Enterprise Edition may additionally depend on FastAPI, PostgreSQL, Redis, Celery, RabbitMQ, MinIO, organization identity providers, NAS cluster services, notification providers, and deployment infrastructure.

## Configuration

Community configuration uses local YAML rules, profiles, presets, output specs, canvas specs, and report output folders.

Enterprise configuration is expected to use environment variables, deployment manifests, identity provider settings, storage backends, audit settings, and commercial license activation mechanisms documented in `docs/15_Commercial/`.

## Example

```bash
mediaqc editions
mediaqc scan ./Media --profile disguise --output ./reports --html
mediaqc transcode ./Media --preset h264_preview --output ./preview --recursive
```

Enterprise-only workflows should be documented with their commercial license assumptions before release.

## Known Limitations

The repository contains enterprise foundation modules for development and evaluation, but production use of Enterprise Edition capabilities requires a commercial license. The current edition model does not yet enforce license activation at runtime.

## Future Improvements

- Add runtime license activation for Enterprise Edition deployments.
- Add clearer package metadata for Community and Enterprise binary distributions.
- Add enterprise feature gates around commercial-only commands before production enterprise release.

## Related Modules

- `mediaqc/editions.py`
- `mediaqc/cli.py`
- `mediaqc/enterprise/`
- `docs/15_Commercial/Licensing.md`
- `README.md`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

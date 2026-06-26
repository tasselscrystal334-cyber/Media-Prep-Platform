# NASWorkflow

## Purpose

Document the NASWorkflow responsibilities in the 16_Operations documentation area.

## Overview

Covers NAS workflow, SHA256 verification, file sync, live deployment checks, media server checks, network checks, remote diagnostics, incident response, and operations troubleshooting.

## Architecture

NAS, SMB, AFP, and NFS workflows are modeled as mounted filesystem paths. `mediaqc/pipeline/` performs path validation, media discovery, SHA256 hashing, FFprobe/MediaInfo metadata, sync, compare, transfer reporting, and package generation without owning OS-level mount credentials.

## Workflow

Mount the NAS share through the operating system, run `mediaqc pipeline sync`, verify with `mediaqc pipeline compare`, and archive or hand off with `mediaqc pipeline package`.

## Dependencies

Python 3.11+, FFmpeg/FFprobe, optional MediaInfo CLI, and OS-mounted SMB/AFP/NFS shares.

## Configuration

Configuration must remain explicit and versionable. Use YAML for rules, profiles, output specs, canvas specs, presets, and future project settings unless an architecture document approves another format.

## Example

```bash
mediaqc pipeline sync ./Media --destination /Volumes/ShowNAS/Media --output ./reports
mediaqc pipeline compare ./Media --destination /Volumes/ShowNAS/Media --output ./reports
```

## Known Limitations

V1.5 does not mount or authenticate NAS shares. Operators must confirm the share is mounted and writable before syncing.

## Future Improvements

Add mount health checks, bandwidth tracking, retry policies, and conflict resolution presets.

## Related Modules

- `README.md`
- `PROJECT_CONSTITUTION.md`
- `docs/01_Architecture/SystemOverview.md`
- `mediaqc/pipeline/network.py`
- `mediaqc/pipeline/sync.py`
- `mediaqc/pipeline/compare.py`

## Revision History

- Documentation version: 1.0
- Last updated: 2026-06-27

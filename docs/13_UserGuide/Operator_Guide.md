# Operator Guide

## Purpose

Provide practical usage for operators preparing media.

## Overview

Operators can scan, watch, generate manifests, verify projects, and open a dashboard.
V1.5 also supports NAS/server pipeline operations for sync, SHA256 comparison, and project package generation.

## Architecture

Operator commands are CLI entry points backed by shared modules.

## Workflow

1. Prepare media in a project folder.
2. Choose a profile or rules file.
3. Run scan.
4. Review reports and dashboard.
5. Generate manifest for delivery.
6. Verify folder integrity before show.

## Dependencies

- Installed `mediaqc` command.
- FFmpeg tools.

## Configuration

Use project profiles or YAML configs under `config/`.

## Example

```bash
mediaqc scan ./Media --profile disguise --output ./reports --html --manifest
mediaqc verify ./Media --manifest ./reports/manifest.json
mediaqc pipeline sync ./Media --destination /Volumes/ShowNAS/Media --profile disguise --output ./reports
mediaqc pipeline compare ./Media --destination /Volumes/ShowNAS/Media --output ./reports
mediaqc pipeline package ./Media --profile disguise --output ./packages
```

## Known Limitations

Warnings should be interpreted in production context; some show workflows intentionally differ from templates.

## Future Improvements

Add screenshots and operator tutorials.

## Related Modules

- `profiles/`
- `config/`

## Revision History

- Documentation version: 0.95

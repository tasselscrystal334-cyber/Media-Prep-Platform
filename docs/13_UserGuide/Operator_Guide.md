# Operator Guide

## Purpose

Provide practical usage for operators preparing media.

## Overview

Operators can scan, watch, generate manifests, verify projects, and open a dashboard.

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

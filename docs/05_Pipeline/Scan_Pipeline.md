# Scan Pipeline

## Purpose

Describe the media scan and report generation pipeline.

## Overview

The scan pipeline turns a media folder into JSON, CSV, HTML, SQLite rows, and optional live event manifests.

## Architecture

Pipeline stages:

1. File discovery.
2. Hash cache lookup or SHA256 calculation.
3. FFprobe metadata extraction.
4. Optional FFmpeg deep decode analysis.
5. Rule/profile validation.
6. Optional live event checks.
7. SQLite persistence.
8. Report writing.

## Workflow

```bash
mediaqc scan ./Media --profile disguise --output ./reports --html
```

## Dependencies

- `mediaqc/scanner.py`
- `mediaqc/database.py`
- `mediaqc/probe.py`
- `mediaqc/report.py`

## Configuration

- `--rules`
- `--profile`
- `--output-spec`
- `--canvas-spec`
- `--deep`
- `--manifest`

## Example

```bash
mediaqc scan ./Media --output-spec ./config/output_spec.yaml --canvas-spec ./config/canvas_spec.yaml --manifest
```

## Known Limitations

Deep decode analysis is intentionally opt-in due to runtime cost.

## Future Improvements

Add parallel scanning controls.

## Related Modules

- `mediaqc/cli.py`

## Revision History

- Documentation version: 0.95

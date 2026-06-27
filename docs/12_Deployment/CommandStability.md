# Command Stability

## Purpose

Define the stable command surface for operators and release packages.

## Overview

Loom keeps existing commands stable and adds aliases only when they reduce operator friction. The stable CLI remains `mediaqc`, with `loom` available as a product-name alias. V2.0 adds root-level `mediaqc doctor`, `mediaqc version`, `mediaqc tools install-check`, `mediaqc tools logs`, and `mediaqc update check`.

## Architecture

Command handlers remain in `mediaqc/cli.py`. Diagnostics live in `mediaqc/diagnostics.py`; update checks live in `mediaqc/updater.py`.

## Workflow

Operators can start with:

```bash
mediaqc version
mediaqc doctor
mediaqc tools install-check
```

## Dependencies

- Typer
- Rich
- FFmpeg tools for doctor checks

## Configuration

Use `--log-dir` or `MEDIAQC_LOG_DIR` to choose where file logs are written.

## Example

```bash
mediaqc --log-dir ./logs tools install-check --json
```

## Known Limitations

Commands that perform network checks may be unavailable in offline venues.

## Future Improvements

Add shell completion installers and command deprecation warnings.

## Related Modules

- `mediaqc/cli.py`
- `mediaqc/diagnostics.py`
- `mediaqc/updater.py`

## Revision History

- Documentation version: 2.0
- Last updated: 2026-06-27

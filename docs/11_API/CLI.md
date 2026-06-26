# CLI API

## Purpose

Document the command-line interface.

## Overview

The CLI command is `mediaqc`.

## Architecture

Commands are implemented in `mediaqc/cli.py`.

## Workflow

Primary commands:

- `scan`
- `watch`
- `db`
- `history`
- `duplicates`
- `manifest`
- `verify`
- `dashboard`

## Dependencies

- Typer
- Rich

## Configuration

CLI options accept paths via `pathlib.Path`.

## Example

```bash
mediaqc scan ./Media --profile disguise --output ./reports --html
```

## Known Limitations

The package command is currently named `mediaqc`.

## Future Improvements

Expose a `mediaprep` alias.

## Related Modules

- `mediaqc/cli.py`

## Revision History

- Documentation version: 0.95

# SQLite Schema

## Purpose

Document the SQLite database used by MediaPrepTool.

## Overview

The default database is `reports/media.db`.

## Architecture

Tables:

- `Project`
- `Media`
- `Hash`
- `History`
- `HashCache`

## Workflow

Scan commands create and update the database automatically.

## Dependencies

- Python standard library `sqlite3`

## Configuration

Use `--database` to choose a database path.

## Example

```bash
mediaqc db --database ./reports/media.db
mediaqc duplicates --database ./reports/media.db
```

## Known Limitations

The database stores latest media rows, not every per-file historical state.

## Future Improvements

Add migrations and per-file scan snapshots.

## Related Modules

- `mediaqc/database.py`

## Revision History

- Documentation version: 0.95

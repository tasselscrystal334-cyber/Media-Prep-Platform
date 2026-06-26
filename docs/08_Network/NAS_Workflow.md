# NAS Workflow

## Purpose

Document future NAS and server synchronization workflows.

## Overview

Manifest files provide the current foundation for NAS sync and show server verification.

## Architecture

Manifest generation is implemented in `mediaqc/live_event/manifest.py`.

## Workflow

```bash
mediaqc manifest ./Media --output ./reports
```

## Dependencies

- SHA256 hashing
- Manifest JSON and CSV outputs

## Configuration

No network configuration exists yet.

## Example

Use `manifest.json` as a transfer checklist.

## Known Limitations

No network copy or remote verification is implemented.

## Future Improvements

Add NAS sync and remote server verify commands.

## Related Modules

- `mediaqc/live_event/manifest.py`
- `mediaqc/live_event/integrity.py`

## Revision History

- Documentation version: 0.95

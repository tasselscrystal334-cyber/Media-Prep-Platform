# GPU Output

## Purpose

Reserve documentation for GPU output and EDID workflows.

## Overview

Current output validation uses YAML project output specs rather than real GPU EDID reads.

## Architecture

Output checks are implemented in `mediaqc/live_event/edid.py`.

## Workflow

```bash
mediaqc scan ./Media --output-spec ./config/output_spec.yaml
```

## Dependencies

- YAML config
- FFprobe metadata

## Configuration

Use `config/output_spec.yaml`.

## Example

Compare media FPS against project refresh rate.

## Known Limitations

No direct GPU or EDID hardware API is implemented.

## Future Improvements

Add platform-specific EDID capture.

## Related Modules

- `mediaqc/live_event/edid.py`

## Revision History

- Documentation version: 0.95

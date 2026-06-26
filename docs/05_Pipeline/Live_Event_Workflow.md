# Live Event Workflow

## Purpose

Document live event-specific media preparation checks.

## Overview

Live event checks validate output specs, canvas layouts, codec playback risk, manifests, and project integrity.

## Architecture

Live event modules live under `mediaqc/live_event/`.

## Workflow

```bash
mediaqc scan ./Media \
  --rules ./config/project_rules.yaml \
  --output-spec ./config/output_spec.yaml \
  --canvas-spec ./config/canvas_spec.yaml \
  --output ./reports \
  --html \
  --manifest
```

## Dependencies

- PyYAML
- FFprobe metadata
- SHA256 hashing

## Configuration

- `config/output_spec.yaml`
- `config/canvas_spec.yaml`
- `config/LED_6400x2000.yaml`
- `config/LED_7680x2160.yaml`
- `config/LED_15360x2160.yaml`

## Example

```bash
mediaqc verify ./Media --manifest ./reports/manifest.json
```

## Known Limitations

EDID validation is currently project output spec validation, not hardware EDID acquisition.

## Future Improvements

Add hardware EDID capture and processor mapping exports.

## Related Modules

- `mediaqc/live_event/edid.py`
- `mediaqc/live_event/canvas.py`
- `mediaqc/live_event/manifest.py`

## Revision History

- Documentation version: 0.95

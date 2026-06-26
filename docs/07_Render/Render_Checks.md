# Render Checks

## Purpose

Document render-facing media checks.

## Overview

Render checks currently focus on codecs, canvas dimensions, frame rate, and decode health.

## Architecture

Render-related checks are distributed across validators, deep analysis, and live event modules.

## Workflow

```bash
mediaqc scan ./Media --deep --canvas-spec ./config/canvas_spec.yaml
```

## Dependencies

- FFmpeg tools
- YAML canvas specs

## Configuration

Use canvas and output specs.

## Example

Validate a 6400x2000 LED canvas before delivery.

## Known Limitations

No GPU render preview is implemented.

## Future Improvements

Add thumbnail generation and visual frame sampling.

## Related Modules

- `mediaqc/deep_analysis.py`
- `mediaqc/live_event/canvas.py`

## Revision History

- Documentation version: 0.95

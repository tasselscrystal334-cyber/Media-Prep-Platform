# HAP

## Purpose

Document HAP handling in MediaPrepTool.

## Overview

HAP codecs are treated as live-event-friendly codecs when paired with suitable pixel formats and canvas sizes.

## Architecture

HAP risk scoring is implemented in `mediaqc/live_event/codec_profiles.py`.

## Workflow

Run:

```bash
mediaqc scan ./Media --html --manifest
```

## Dependencies

- FFprobe metadata.

## Configuration

Profiles may allow `hap`, `hap_alpha`, `hap_q`, and `hap_q_alpha`.

## Example

HAP Alpha material should use alpha-capable variants. If the codec name suggests alpha but pixel format metadata does not confirm alpha, Loom reports WARN instead of FAIL.

## Known Limitations

Alpha detection is heuristic when ffprobe does not expose alpha information.

## Future Improvements

Add frame sampling for alpha-channel confirmation.

## Related Modules

- `mediaqc/live_event/codec_profiles.py`

## Revision History

- Documentation version: 0.95

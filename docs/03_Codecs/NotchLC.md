# NotchLC

## Purpose

Document NotchLC handling.

## Overview

NotchLC is treated as a preferred real-time playback codec for large and live event canvases.

## Architecture

Codec profile analysis records codec, pixel format, width, height, FPS, and bit rate for NotchLC media.

## Workflow

Use live event scan options to include codec risk summary.

## Dependencies

- FFprobe metadata.

## Configuration

Profiles may include `notchlc` in `allowed_codecs`.

## Example

```yaml
video:
  allowed_codecs: [notchlc, hap, prores]
```

## Known Limitations

No NotchLC encoder-specific validation is implemented.

## Future Improvements

Add NotchLC-specific frame and bandwidth heuristics.

## Related Modules

- `mediaqc/live_event/codec_profiles.py`

## Revision History

- Documentation version: 0.95

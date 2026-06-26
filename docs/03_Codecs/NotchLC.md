# NotchLC

## Purpose

Document NotchLC handling.

## Overview

NotchLC is treated as a preferred real-time playback codec for large and live event canvases.
Encoding support is optional and must use official routes only: Adobe Media Encoder, Adobe Premiere, Adobe After Effects, or official NotchLC SDK/tools legally obtained by the user.

## Architecture

Codec profile analysis records codec, pixel format, width, height, FPS, and bit rate for NotchLC media.
Adobe plugin workflows are represented as watch-folder preparation in `mediaqc/processing/adobe_ame.py`. MediaPrep Studio does not load or inspect Adobe plugin binaries.

## Workflow

Use live event scan options to include codec risk summary.
Use `mediaqc notchlc prepare` to prepare an Adobe Media Encoder Watch Folder:

```bash
mediaqc notchlc prepare ./Media --watch-folder ./AME_Watch --output ./Encoded_NotchLC
```

## Dependencies

- FFprobe metadata.
- Adobe Media Encoder and official NotchLC Adobe plugin when using the AME workflow.

## Configuration

Profiles may include `notchlc` in `allowed_codecs`. Optional encoder backend settings live in `config/encoder_backends.yaml`.

## Example

```yaml
video:
  allowed_codecs: [notchlc, hap, prores]
```

## Known Limitations

No Adobe plugin binary is reverse engineered, decompiled, patched, recompiled, loaded, or called directly. AME detection is best-effort and plugin availability is only a filesystem hint.

## Future Improvements

Add NotchLC-specific frame and bandwidth heuristics.
Add official SDK/tool integration if a documented and legally available command-line encoder is provided by the user.

## Related Modules

- `mediaqc/live_event/codec_profiles.py`
- `mediaqc/processing/adobe_ame.py`
- `mediaqc/processing/encoder_backends.py`

## Revision History

- Documentation version: 0.95
- Last updated: 2026-06-27

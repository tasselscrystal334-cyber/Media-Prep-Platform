# ProRes

## Purpose

Document ProRes handling.

## Overview

ProRes is treated as a recommended production codec, especially for quality-focused and alpha workflows.

## Architecture

ProRes category and risk scoring are handled in `codec_profiles.py`.

## Workflow

Use project profiles or rules to allow ProRes.

## Dependencies

- FFprobe metadata.

## Configuration

Profiles may include `prores`.

## Example

Transparent material should prefer ProRes 4444 or an alpha-capable HAP variant.

## Known Limitations

ProRes profile variants are inferred from codec metadata where available.

## Future Improvements

Add ProRes profile parsing and alpha-specific checks.

## Related Modules

- `mediaqc/live_event/codec_profiles.py`

## Revision History

- Documentation version: 0.95

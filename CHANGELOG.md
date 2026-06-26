# Changelog

## Purpose

Track released project changes without preserving short-lived development logs.

## Overview

This changelog records the current documented release state only. Completed task chatter, bug archaeology, discarded plans, and obsolete implementation notes are intentionally excluded.

## Architecture

Changes are grouped by product capability and linked to repository documentation where possible.

## Workflow

Update this file whenever implementation changes are merged into the repository documentation set.

## Dependencies

No runtime dependencies.

## Configuration

No configuration.

## Example

```text
0.95.0 - Live Event Media QC Extension
```

## Known Limitations

This file records release-level changes only.

## Future Improvements

Add release artifact links when packaging is introduced.

## Related Modules

- `README.md`
- `docs/15_Roadmap/Product_Roadmap.md`

## Revision History

### 0.95.0

- Added Live Event output specification checks.
- Added canvas validation.
- Added codec risk profiles for HAP, NotchLC, ProRes, H264, HEVC, and other codecs.
- Added manifest generation and integrity verification.
- Added dashboard REST API and documentation structure.

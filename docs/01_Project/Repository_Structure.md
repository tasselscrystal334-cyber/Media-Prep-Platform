# Repository Structure

## Purpose

Document the target GitHub repository structure for MediaPrepTool.

## Overview

The repository separates source code, tests, documentation, assets, examples, and scripts.

## Architecture

Target structure:

```text
MediaPrepTool/
  docs/
    01_Project/
    02_Architecture/
    03_Codecs/
    04_UI/
    05_Pipeline/
    06_GPU/
    07_Render/
    08_Network/
    09_Plugins/
    10_Testing/
    11_API/
    12_Deployment/
    13_UserGuide/
    14_Examples/
    15_Roadmap/
  src/
  tests/
  assets/
  examples/
  scripts/
  README.md
  CHANGELOG.md
  ROADMAP.md
```

## Workflow

New modules require matching documentation updates in the relevant `docs/` category.

## Dependencies

No runtime dependencies.

## Configuration

No configuration.

## Example

Codec changes belong in `docs/03_Codecs/`.

## Known Limitations

The Python package currently remains under `mediaqc/`; `src/` is reserved for future source layout migration.

## Future Improvements

Move package code under `src/` when package distribution is hardened.

## Related Modules

- `docs/01_Project/GitHub_Documentation_Workflow.md`

## Revision History

- Documentation version: 0.95

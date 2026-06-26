# GitHub Documentation Workflow

## Purpose

Make the GitHub repository the single source of truth for project architecture, standards, APIs, workflows, and technical decisions.

## Overview

Chat history is not permanent documentation. Every durable decision must be captured in repository Markdown files.

## Architecture

Documentation is organized by domain:

- `01_Project`: project policy and governance.
- `02_Architecture`: system design.
- `03_Codecs`: codec and FFmpeg notes.
- `05_Pipeline`: scan and live event pipeline.
- `08_Database`: SQLite schema and data flow.
- `10_Testing`: test strategy.
- `11_API`: CLI and REST API.
- `13_UserGuide`: operator-facing usage.

## Workflow

Every feature follows:

```text
Design -> Documentation -> Implementation -> Tests -> Documentation Update
```

## Dependencies

No runtime dependencies.

## Configuration

No configuration.

## Example

When adding a new validator, update architecture, API or user guide docs, implement the validator, add tests, then update docs if behavior changed.

## Known Limitations

The workflow is currently enforced by convention rather than CI.

## Future Improvements

Add documentation checks to CI.

## Related Modules

- `CONTRIBUTING.md`
- `docs/02_Architecture/System_Architecture.md`

## Revision History

- Documentation version: 0.95

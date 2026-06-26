# Contributing

## Purpose

Define the engineering and documentation workflow for contributors.

## Overview

All implementation changes must be reflected in repository documentation. Chat history is not permanent documentation.

## Architecture

Contributions should follow the existing modules before introducing new subsystems:

- CLI in `mediaqc/cli.py`
- Validation in `mediaqc/validators/`
- Live event extensions in `mediaqc/live_event/`
- Dashboard API in `mediaqc/dashboard.py`

## Workflow

1. Read relevant docs.
2. Design the change.
3. Update or create documentation.
4. Implement the change.
5. Add tests.
6. Update documentation again if implementation differs from design.

## Dependencies

Use `requirements.txt` for Python dependencies.

## Configuration

Use YAML for project rules, profiles, output specs, and canvas specs.

## Example

```bash
python -m pytest
```

## Known Limitations

There is no automated documentation linter yet.

## Future Improvements

- Add pre-commit checks.
- Add documentation coverage checks.

## Related Modules

- `docs/01_Project/GitHub_Documentation_Workflow.md`
- `docs/10_Testing/Testing_Strategy.md`

## Revision History

- Documentation version: 0.95

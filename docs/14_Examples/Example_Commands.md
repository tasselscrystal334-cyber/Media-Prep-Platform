# Example Commands

## Purpose

Collect common command examples without duplicating full user guide content.

## Overview

Examples assume the command is installed as `mediaqc`.

## Architecture

Examples invoke existing CLI commands.

## Workflow

Use the command matching the production task.

## Dependencies

- Installed CLI
- FFmpeg tools

## Configuration

Examples reference `profiles/` and `config/`.

## Example

```bash
mediaqc scan ./Media --profile disguise --output ./reports --html
mediaqc watch ./Media --profile disguise --output ./reports
mediaqc dashboard --database ./reports/media.db
mediaqc manifest ./Media --output ./reports
mediaqc verify ./Media --manifest ./reports/manifest.json
```

## Known Limitations

Paths should be adapted per project.

## Future Improvements

Add platform-specific examples.

## Related Modules

- `docs/13_UserGuide/Operator_Guide.md`

## Revision History

- Documentation version: 0.95

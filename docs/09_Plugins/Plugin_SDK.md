# Plugin SDK

## Purpose

Document the current plugin extension point.

## Overview

The validation engine supports external validators through registration.

## Architecture

Validators inherit `BaseValidator` and return `ValidationResult`.

## Workflow

Register a validator class through the `mediaqc.validators` Python entry point group or by calling `register_validator()`.

## Dependencies

- Python packaging entry points

## Configuration

Enable or disable validators in YAML:

```yaml
validators:
  codec: true
```

## Example

Create a custom validator that subclasses `BaseValidator`.

## Known Limitations

No standalone plugin template is provided yet.

## Future Improvements

Add sample plugin packages.

## Related Modules

- `mediaqc/validation_engine.py`
- `mediaqc/validators/__init__.py`

## Revision History

- Documentation version: 0.95

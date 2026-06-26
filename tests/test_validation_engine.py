from mediaqc.validation_engine import discover_validators
from mediaqc.validators import BaseValidator, ValidationResult


def test_discover_validators_loads_builtins() -> None:
    validators = discover_validators()

    assert {
        "codec",
        "resolution",
        "framerate",
        "colorspace",
        "pixfmt",
        "bitrate",
        "audio",
        "filename",
        "filesize",
        "folder_structure",
    }.issubset(validators)
    assert issubclass(validators["codec"], BaseValidator)


def test_validation_result_to_dict() -> None:
    result = ValidationResult(
        validator="codec",
        status="PASS",
        severity="FAIL",
        message="ok",
        details={"actual": "hap"},
    )

    assert result.to_dict() == {
        "validator": "codec",
        "status": "PASS",
        "severity": "FAIL",
        "message": "ok",
        "details": {"actual": "hap"},
    }

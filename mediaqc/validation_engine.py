"""Media validation engine."""

from __future__ import annotations

import importlib
import pkgutil
from importlib.metadata import entry_points

import mediaqc.validators as validators_pkg
from .models import MediaFileResult
from .rules import ProjectRules
from .validators import BaseValidator, VALIDATOR_REGISTRY, ValidationResult, register_validator


class ValidationEngine:
    """Load validators and run enabled validation checks."""

    def __init__(self, rules: ProjectRules) -> None:
        self.rules = rules
        self.validator_classes = discover_validators()

    def enabled_validators(self) -> list[BaseValidator]:
        enabled: list[BaseValidator] = []
        for name in sorted(self.validator_classes):
            is_enabled = self.rules.validators.get(name, True)
            if is_enabled:
                enabled.append(self.validator_classes[name](self.rules))
        return enabled

    def validate(self, media: MediaFileResult) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        for validator in self.enabled_validators():
            try:
                results.append(validator.validate(media))
            except Exception as exc:  # noqa: BLE001 - validators must not stop a scan.
                results.append(
                    validator.result(
                        "FAIL",
                        f"Validator '{validator.name}' crashed: {exc}",
                        {"exception": exc.__class__.__name__},
                    )
                )
        return results

    def apply(self, media: MediaFileResult) -> None:
        results = self.validate(media)
        media.validation_results = results
        media.warnings.clear()
        media.failures.clear()

        if media.status == "FAIL":
            media.failures.append("File processing failed; rule checks may be incomplete.")

        for result in results:
            if result.status == "FAIL":
                media.failures.append(f"{result.validator}: {result.message}")
            elif result.status == "WARN":
                media.warnings.append(f"{result.validator}: {result.message}")

        if media.failures:
            media.rule_status = "FAIL"
        elif media.warnings:
            media.rule_status = "WARN"
        else:
            media.rule_status = "PASS"


def discover_validators() -> dict[str, type[BaseValidator]]:
    """Import built-ins and entry-point plugins, then return the registry."""

    _import_builtin_validators()
    _load_entry_point_validators()
    return dict(VALIDATOR_REGISTRY)


def _import_builtin_validators() -> None:
    for module_info in pkgutil.iter_modules(validators_pkg.__path__):
        if module_info.name.startswith("_"):
            continue
        importlib.import_module(f"{validators_pkg.__name__}.{module_info.name}")


def _load_entry_point_validators() -> None:
    try:
        eps = entry_points(group="mediaqc.validators")
    except TypeError:
        eps = entry_points().get("mediaqc.validators", [])

    for entry_point in eps:
        loaded = entry_point.load()
        if isinstance(loaded, type) and issubclass(loaded, BaseValidator):
            register_validator(loaded)

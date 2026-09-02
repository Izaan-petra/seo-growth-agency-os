"""Dependency-free validation for the JSON Schema subset used by SEO OS.

The schema documents declare JSON Schema 2020-12. This validator intentionally
implements only the keywords used by the Batch 1 contracts so the foundation can
run without downloading dependencies. A later runtime may add a full validator
without changing the public ``validate_instance`` interface.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    path: str
    message: str


class SchemaValidationError(ValueError):
    def __init__(self, schema_name: str, issues: Sequence[ValidationIssue]) -> None:
        self.schema_name = schema_name
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.path}: {issue.message}" for issue in self.issues)
        super().__init__(f"{schema_name} validation failed: {detail}")


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schema_path(schema_name: str) -> Path:
    safe_name = schema_name.removesuffix(".schema.json")
    if not re.fullmatch(r"[a-z0-9-]+", safe_name):
        raise ValueError(f"Invalid schema name: {schema_name}")
    return repository_root() / "schemas" / f"{safe_name}.schema.json"


def load_schema(schema_name: str) -> Mapping[str, Any]:
    path = schema_path(schema_name)
    with path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    if not isinstance(schema, dict):
        raise ValueError(f"Schema must be a JSON object: {path}")
    return schema


def validate_instance(schema_name: str, instance: Any) -> None:
    issues: list[ValidationIssue] = []
    _validate(load_schema(schema_name), instance, "$", issues)
    if issues:
        raise SchemaValidationError(schema_name, issues)


def _validate(
    schema: Mapping[str, Any], instance: Any, path: str, issues: list[ValidationIssue]
) -> None:
    expected_type = schema.get("type")
    if expected_type is not None and not _matches_type(expected_type, instance):
        issues.append(ValidationIssue(path, f"expected type {expected_type!r}"))
        return

    if "const" in schema and instance != schema["const"]:
        issues.append(ValidationIssue(path, f"must equal {schema['const']!r}"))
    if "enum" in schema and instance not in schema["enum"]:
        issues.append(ValidationIssue(path, f"must be one of {schema['enum']!r}"))

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                issues.append(ValidationIssue(path, f"missing required property {key!r}"))

        properties = schema.get("properties", {})
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                _validate(properties[key], value, child_path, issues)
            elif schema.get("additionalProperties") is False:
                issues.append(ValidationIssue(child_path, "additional property is not allowed"))
            elif isinstance(schema.get("additionalProperties"), dict):
                _validate(schema["additionalProperties"], value, child_path, issues)

    if isinstance(instance, list):
        minimum = schema.get("minItems")
        if minimum is not None and len(instance) < minimum:
            issues.append(ValidationIssue(path, f"must contain at least {minimum} items"))
        maximum = schema.get("maxItems")
        if maximum is not None and len(instance) > maximum:
            issues.append(ValidationIssue(path, f"must contain at most {maximum} items"))
        if schema.get("uniqueItems"):
            encoded = [json.dumps(value, sort_keys=True) for value in instance]
            if len(encoded) != len(set(encoded)):
                issues.append(ValidationIssue(path, "items must be unique"))
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                _validate(item_schema, value, f"{path}[{index}]", issues)

    if isinstance(instance, str):
        minimum = schema.get("minLength")
        if minimum is not None and len(instance) < minimum:
            issues.append(ValidationIssue(path, f"must be at least {minimum} characters"))
        maximum = schema.get("maxLength")
        if maximum is not None and len(instance) > maximum:
            issues.append(ValidationIssue(path, f"must be at most {maximum} characters"))
        pattern = schema.get("pattern")
        if pattern is not None and re.search(pattern, instance) is None:
            issues.append(ValidationIssue(path, f"does not match pattern {pattern!r}"))
        format_name = schema.get("format")
        if format_name and not _valid_format(format_name, instance):
            issues.append(ValidationIssue(path, f"invalid {format_name} value"))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            issues.append(ValidationIssue(path, f"must be at least {minimum}"))
        maximum = schema.get("maximum")
        if maximum is not None and instance > maximum:
            issues.append(ValidationIssue(path, f"must be at most {maximum}"))


def _matches_type(expected: str | Sequence[str], instance: Any) -> bool:
    expected_types = (expected,) if isinstance(expected, str) else tuple(expected)
    return any(_matches_single_type(value, instance) for value in expected_types)


def _matches_single_type(expected: str, instance: Any) -> bool:
    mapping = {
        "null": lambda value: value is None,
        "boolean": lambda value: isinstance(value, bool),
        "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
        "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
        "string": lambda value: isinstance(value, str),
        "array": lambda value: isinstance(value, list),
        "object": lambda value: isinstance(value, dict),
    }
    try:
        return mapping[expected](instance)
    except KeyError as exc:
        raise ValueError(f"Unsupported schema type: {expected}") from exc


def _valid_format(format_name: str, value: str) -> bool:
    try:
        if format_name == "date":
            date.fromisoformat(value)
            return True
        if format_name == "date-time":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "T" in value
        if format_name == "uri":
            parsed = urlparse(value)
            return bool(parsed.scheme and parsed.netloc)
    except ValueError:
        return False
    return True

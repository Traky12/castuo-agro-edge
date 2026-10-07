"""JSON Schema validation for Evidence Bridge event types.

jsonschema's Draft7Validator only checks "format" when a format-checking library
for that format is installed — "date-time" needs the optional rfc3339-validator
package, which this repo doesn't otherwise need. Rather than pull in a dependency
for one format keyword, date-time fields declared in the schema are re-checked
explicitly below with datetime.fromisoformat.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import jsonschema

_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _load_schema(name: str) -> dict:
    with open(_SCHEMA_DIR / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


_TELEMETRY_EVENT_SCHEMA = _load_schema("telemetry_event.schema.json")
_DEVIATION_SCHEMA = _load_schema("deviation.schema.json")
_REVIEW_ACTION_SCHEMA = _load_schema("review_action.schema.json")
_EVIDENCE_MANIFEST_SCHEMA = _load_schema("evidence_manifest.schema.json")


@dataclass
class ValidationResult:
    valid: bool
    line_number: int
    event: Optional[dict]
    errors: list = field(default_factory=list)


def _date_time_fields(schema: dict) -> list:
    return [
        name
        for name, prop in schema.get("properties", {}).items()
        if prop.get("format") == "date-time"
    ]


def _check_date_time_fields(raw: dict, schema: dict) -> list:
    errors = []
    for name in _date_time_fields(schema):
        value = raw.get(name)
        if value is None:
            continue
        try:
            datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"'{name}': {value!r} is not a valid date-time")
    return errors


def _validate(raw: dict, schema: dict, line_number: int) -> ValidationResult:
    validator = jsonschema.Draft7Validator(schema)
    errors = [e.message for e in sorted(validator.iter_errors(raw), key=lambda e: list(e.path))]
    if isinstance(raw, dict):
        errors += _check_date_time_fields(raw, schema)
    if errors:
        return ValidationResult(valid=False, line_number=line_number, event=None, errors=errors)
    return ValidationResult(valid=True, line_number=line_number, event=raw, errors=[])


def validate_telemetry_event(raw: dict, line_number: int = 0) -> ValidationResult:
    return _validate(raw, _TELEMETRY_EVENT_SCHEMA, line_number)


def validate_deviation(raw: dict, line_number: int = 0) -> ValidationResult:
    return _validate(raw, _DEVIATION_SCHEMA, line_number)


def validate_review_action(raw: dict, line_number: int = 0) -> ValidationResult:
    return _validate(raw, _REVIEW_ACTION_SCHEMA, line_number)


def validate_evidence_manifest(raw: dict, line_number: int = 0) -> ValidationResult:
    return _validate(raw, _EVIDENCE_MANIFEST_SCHEMA, line_number)

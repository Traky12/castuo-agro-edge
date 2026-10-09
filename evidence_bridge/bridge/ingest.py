"""Ingest raw telemetry events from a JSONL source and validate each line.

Read-only: this module never writes to the source. Malformed JSON and schema
violations are reported per line, never silently dropped or auto-corrected.
"""

import json
from pathlib import Path
from typing import Iterator

from evidence_bridge.bridge.validate import ValidationResult, validate_telemetry_event


def ingest_jsonl(path: Path) -> Iterator[ValidationResult]:
    with open(path, "r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            yield _ingest_line(line, line_number)


def _ingest_line(line: str, line_number: int) -> ValidationResult:
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as exc:
        return ValidationResult(valid=False, line_number=line_number, event=None,
                                 errors=[f"malformed JSON: {exc}"])
    return validate_telemetry_event(raw, line_number=line_number)

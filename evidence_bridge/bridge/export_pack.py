"""Deterministic offline Evidence Bridge pack export.

Only accepts pre-hashed, schema-valid, consecutive synthetic/local events.
A pack is not a signature, independent verification, or an authorization.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

from evidence_bridge.bridge.validate import validate_evidence_manifest, validate_telemetry_event
from evidence_bridge.bridge.provenance import canonical_form, compute_event_hash

_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
_FORMAT = "EB-POC-001-PORTABLE-V1"


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def export_pack(
    events: Iterable[dict], output_dir: Path, *,
    source_commit: str, generated_at: str, operation_scope_id: str,
) -> dict:
    """Write a new, non-overwriting package without external network or services."""
    if not _COMMIT.fullmatch(source_commit):
        raise ValueError("source_commit must be exact 40-character lowercase Git SHA")
    try:
        dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("timezone required")
    except (TypeError, ValueError) as exc:
        raise ValueError("generated_at must be an ISO 8601 timestamp with timezone") from exc
    if not isinstance(operation_scope_id, str) or not operation_scope_id:
        raise ValueError("operation_scope_id is required")
    values = list(events)
    if not values or len(values) > 10000:
        raise ValueError("1..10000 events are required")
    previous = None
    seen: set[str] = set()
    entries: list[dict] = []
    for i, event in enumerate(values, 1):
        if not isinstance(event, dict):
            raise ValueError(f"event {i} must be object")
        checked = validate_telemetry_event(event)
        if not checked.valid:
            raise ValueError(f"event {i} schema invalid: {checked.errors}")
        ident = event["event_id"]
        if ident in seen:
            raise ValueError("duplicate event_id")
        seen.add(ident)
        if event["operation_scope_id"] != operation_scope_id:
            raise ValueError("cross-scope event rejected")
        if event.get("previous_event_hash") != previous:
            raise ValueError(f"event {i} chain predecessor mismatch")
        actual = event.get("payload_hash")
        if not isinstance(actual, str) or not _HASH.fullmatch(actual) or actual != compute_event_hash(event):
            raise ValueError(f"event {i} hash invalid or missing")
        entries.append({
            "event_id": ident, "payload_hash": actual, "previous_event_hash": previous,
        })
        previous = actual
    raw = b"".join(canonical(event) + b"\n" for event in values)
    manifest = {
        "format_version": _FORMAT,
        "manifest_id": f"{operation_scope_id}-portable-v1",
        "operation_scope_id": operation_scope_id,
        "source_commit": source_commit,
        "generated_at": generated_at,
        "file_count": 1,
        "files": [{"path": "events.jsonl", "sha256": digest(raw)}],
        "entries": entries,
    }
    manifest["manifest_hash"] = digest(canonical(manifest))
    verified = validate_evidence_manifest(manifest)
    if not verified.valid:
        raise ValueError(f"manifest violates schema: {verified.errors}")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    (output / "events.jsonl").write_bytes(raw)
    (output / "manifest.json").write_bytes(canonical(manifest) + b"\n")
    return {
        "status": "EXPORTED_LOCAL_UNREVIEWED",
        "pack_dir": str(output),
        "events": len(values),
        "manifest_hash": manifest["manifest_hash"],
        "promotion": "BLOCKED",
    }

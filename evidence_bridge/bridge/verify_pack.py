"""Independent stdlib verifier for EB-POC-001 local evidence packs.

Does not call the exporter, connect to a network, or approve events.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_MAX_BYTES = 10 * 1024 * 1024
_FORMAT = "EB-POC-001-PORTABLE-V1"
_FIELDS = {
    "format_version", "manifest_id", "operation_scope_id", "source_commit",
    "generated_at", "file_count", "files", "entries", "manifest_hash",
}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _read(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("required pack file missing or symlinked")
    if path.stat().st_size > _MAX_BYTES:
        raise ValueError("pack file exceeds 10 MiB")
    return path.read_bytes()


def verify_pack(pack_dir: Path) -> dict:
    """Fail closed on any altered file, event, scope, or chain."""
    try:
        root = Path(pack_dir)
        manifest = json.loads(_read(root / "manifest.json"))
        raw = _read(root / "events.jsonl")
        if not isinstance(manifest, dict) or set(manifest) != _FIELDS:
            raise ValueError("manifest fields mismatch")
        if manifest["format_version"] != _FORMAT:
            raise ValueError("unsupported format version")
        if not isinstance(manifest["source_commit"], str) or not _SHA.fullmatch(manifest["source_commit"]):
            raise ValueError("source_commit invalid")
        declared = manifest["manifest_hash"]
        if not isinstance(declared, str) or not _HASH.fullmatch(declared):
            raise ValueError("manifest hash syntax invalid")
        unsigned = {key: val for key, val in manifest.items() if key != "manifest_hash"}
        if _digest(_canonical(unsigned)) != declared:
            raise ValueError("manifest hash mismatch")
        if manifest["file_count"] != 1 or manifest["files"] != [
            {"path": "events.jsonl", "sha256": _digest(raw)}
        ]:
            raise ValueError("file digest/count/path mismatch")
        items = raw.splitlines(keepends=True)
        if not items or len(items) > 10000 or any(not row.endswith(b"\n") for row in items):
            raise ValueError("events.jsonl empty/oversized or missing newline")
        events = [json.loads(row) for row in items]
        if b"".join(_canonical(ev) + b"\n" for ev in events) != raw:
            raise ValueError("events not canonical JSONL")
        if not isinstance(manifest["entries"], list) or len(manifest["entries"]) != len(events):
            raise ValueError("entry count mismatch")
        previous = None
        seen: set[str] = set()
        for ev, entry in zip(events, manifest["entries"]):
            if not isinstance(ev, dict) or not isinstance(entry, dict):
                raise ValueError("event/entry invalid")
            if set(entry) != {"event_id", "payload_hash", "previous_event_hash"}:
                raise ValueError("entry fields mismatch")
            event_id = ev.get("event_id")
            if not isinstance(event_id, str) or not event_id or event_id in seen:
                raise ValueError("duplicate/invalid event ID")
            seen.add(event_id)
            if ev.get("operation_scope_id") != manifest["operation_scope_id"]:
                raise ValueError("cross-scope event")
            if ev.get("previous_event_hash") != previous:
                raise ValueError("chain broken")
            claimed = ev.get("payload_hash")
            unsigned_event = {k: v for k, v in ev.items() if k != "payload_hash"}
            if not isinstance(claimed, str) or not _HASH.fullmatch(claimed) or _digest(_canonical(unsigned_event)) != claimed:
                raise ValueError("event payload altered")
            if entry != {
                "event_id": event_id,
                "payload_hash": claimed,
                "previous_event_hash": previous,
            }:
                raise ValueError("manifest entry does not match event")
            previous = claimed
        return {
            "status": "VALID_LOCAL_INTEGRITY_ONLY",
            "events": len(events),
            "manifest_hash": declared,
            "promotion": "BLOCKED",
            "independent_review": "PENDING",
        }
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return {
            "status": "INVALID",
            "reason": str(exc),
            "promotion": "BLOCKED",
            "independent_review": "PENDING",
        }

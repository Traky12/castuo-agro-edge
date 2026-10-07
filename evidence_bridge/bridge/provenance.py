"""Canonical hashing and hash-chaining for ingested telemetry events.

payload_hash covers every field except itself, including previous_event_hash —
so the chain link is part of what's hashed, and altering an earlier event or
splicing the chain breaks verification on everything downstream of it.
"""

import hashlib
import json
from typing import Optional

_HASH_EXCLUDED_FIELDS = {"payload_hash"}


def canonical_form(event: dict) -> bytes:
    payload = {k: v for k, v in event.items() if k not in _HASH_EXCLUDED_FIELDS}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def compute_event_hash(event: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_form(event)).hexdigest()


def apply_provenance(event: dict, previous_event_hash: Optional[str] = None) -> dict:
    """Return a copy of event stamped with previous_event_hash and payload_hash."""
    stamped = dict(event)
    stamped["previous_event_hash"] = previous_event_hash
    stamped["payload_hash"] = compute_event_hash(stamped)
    return stamped


def verify_event_hash(event: dict) -> bool:
    """True if event['payload_hash'] matches a fresh recomputation — false if tampered or absent."""
    expected = event.get("payload_hash")
    if not expected:
        return False
    return compute_event_hash(event) == expected

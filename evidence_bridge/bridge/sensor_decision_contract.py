"""Bounded offline sensor observation -> human-review candidate.

No input is implicitly trusted, no agronomic threshold is inferred, no actuation.
The caller must enforce authenticated source ownership and tenant identity.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime

_TENANT = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SENSOR_KINDS = frozenset({
    "fruit_diameter", "trunk_diameter", "sap_flow", "leaf_temperature",
    "soil_probe", "weather_station",
})
_REQUIRED = frozenset({
    "tenant_id", "sensor_kind", "observed_at", "value", "unit",
    "source_record_sha256",
})


def observation_to_review_candidate(
    observation: dict, *, authenticated_tenant_id: str,
    authorized_source: bool,
) -> dict:
    """Create a *non-executable* synthetic/local observation, never a decision.

    Caller-provided authenticated_tenant_id and authorized_source must come from
    authenticated server-side context, never from untrusted payload fields.
    """
    if not isinstance(observation, dict) or set(observation) != _REQUIRED:
        raise ValueError("observation fields are missing or not allowed")
    if not isinstance(authenticated_tenant_id, str) or not _TENANT.fullmatch(authenticated_tenant_id):
        raise ValueError("authenticated tenant is required")
    if type(authorized_source) is not bool or not authorized_source:
        raise PermissionError("source authorization must be verified by caller")
    tenant_id = observation["tenant_id"]
    if not isinstance(tenant_id, str) or not _TENANT.fullmatch(tenant_id) or tenant_id != authenticated_tenant_id:
        raise PermissionError("tenant mismatch")
    kind = observation["sensor_kind"]
    if not isinstance(kind, str) or kind not in _SENSOR_KINDS:
        raise ValueError("sensor kind unsupported")
    stamp = observation["observed_at"]
    if not isinstance(stamp, str):
        raise ValueError("timezone-aware timestamp required")
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if parsed.utcoffset() is None:
        raise ValueError("timestamp timezone missing")
    value = observation["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("nonfinite or nonnumeric measurement")
    unit = observation["unit"]
    if not isinstance(unit, str) or not 1 <= len(unit) <= 24 or any(ord(c) < 32 for c in unit):
        raise ValueError("invalid unit")
    digest = observation["source_record_sha256"]
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        raise ValueError("source record digest required")
    # Reject arbitrary metadata, credentials, commands or third-party telemetry.
    body = json.dumps(observation, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {
        "contract": "castuo.sensor-review-candidate.v1",
        "candidate_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "tenant_id": tenant_id,
        "sensor_kind": kind,
        "observed_at": stamp,
        "source_record_sha256": digest,
        "review_state": "PENDING_HUMAN",
        "evidence_verified": False,
        "recommendation": None,
        "automatic_execution": False,
        "promotion": "BLOCKED",
    }

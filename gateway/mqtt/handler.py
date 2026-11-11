"""Inbound MQTT message handling for the pilot gateway: validate, de-duplicate, buffer.

Pilot profile: OBSERVATION ONLY. Nothing here, or anywhere in the pilot path, executes
a command. Messages on command/actuation topics are refused before their payload is read.

Every message ends in a Decision. A rejection always carries a reason and leaves the
buffer untouched, so a caller can count and log it; nothing is dropped silently.

Standard library only: this module is imported both as `gateway.mqtt.handler` (tests)
and as a top-level `handler` (the daemon runs from this directory, like db.py/sync.py).

The accepted reading format and the closed metric/unit list below are the synthetic
pilot profile. They say what the gateway will buffer, not that a reading is correct,
calibrated or fit for an agronomic decision.
"""
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

ALLOWED_UNITS = {
    "temperature": frozenset({"degC"}),
    "humidity": frozenset({"pct"}),
    "soil_moisture": frozenset({"pct"}),
    "co2": frozenset({"ppm"}),
    "ph": frozenset({"pH"}),
    "ec": frozenset({"uS/cm"}),
    "luminosity": frozenset({"lux"}),
}
READING_FIELDS = frozenset({"device_id", "metric", "value", "unit", "occurred_at"})
_ACTUATION_SEGMENTS = frozenset({"commands", "command", "actuators", "actuator"})


@dataclass(frozen=True)
class Decision:
    accepted: bool
    reason: str


ACCEPTED = Decision(True, "accepted")


def _reject(reason: str) -> Decision:
    return Decision(False, reason)


def is_actuation_topic(topic: str) -> bool:
    """True for any topic that looks like a command channel: commands/actuators level, or a trailing /set."""
    parts = [part.lower() for part in str(topic).split("/")]
    return bool(_ACTUATION_SEGMENTS.intersection(parts)) or parts[-1] == "set"


def _decode(raw):
    if isinstance(raw, (bytes, bytearray)):
        return bytes(raw).decode("utf-8")
    return raw


def _source_key(device_id: str, metric: str, occurred_at_utc: str, value: float) -> str:
    """Identity of a physical reading, independent of when or how often it was delivered."""
    return hashlib.sha256(f"{device_id}|{metric}|{occurred_at_utc}|{json.dumps(value)}".encode()).hexdigest()


def process_message(topic: str, raw, db, *, now: Optional[datetime] = None) -> Decision:
    """Validate one inbound message and buffer it if (and only if) it is a valid, new reading."""
    if is_actuation_topic(topic):
        return _reject("actuation_topic_rejected")
    try:
        body = json.loads(_decode(raw))
    except (ValueError, UnicodeDecodeError, TypeError):
        return _reject("malformed_json")
    if not isinstance(body, dict):
        return _reject("not_an_object")
    if set(body) - READING_FIELDS:
        return _reject("unexpected_fields")

    device_id = body.get("device_id")
    if not isinstance(device_id, str) or not device_id.strip():
        return _reject("missing_device_id")
    metric = body.get("metric")
    if not isinstance(metric, str) or metric not in ALLOWED_UNITS:
        return _reject("unknown_metric")
    unit = body.get("unit")
    if not isinstance(unit, str) or unit not in ALLOWED_UNITS[metric]:
        return _reject("unknown_unit")
    value = body.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return _reject("value_not_numeric")
    if not math.isfinite(value):
        return _reject("non_finite_value")
    stamp = body.get("occurred_at")
    if not isinstance(stamp, str):
        return _reject("occurred_at_invalid")
    try:
        occurred = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return _reject("occurred_at_invalid")
    if occurred.utcoffset() is None:
        return _reject("occurred_at_missing_timezone")

    key = _source_key(device_id, metric, occurred.astimezone(timezone.utc).isoformat(), float(value))
    if not db.enqueue(topic, body, source_key=key, now=now):
        return _reject("duplicate_source_key")
    return ACCEPTED

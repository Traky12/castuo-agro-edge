"""Gateway buffer rows -> Evidence Bridge telemetry events (read-only, offline).

Turns what the gateway actually buffered and delivered into the events the pack exporter
accepts. The hash chain is computed here, at export time, in `seq` order: ingestion never
depends on it, and the same rows always give the same chain.

Hashes prove the events were not altered after export. They do NOT prove the readings are
correct, the sensor was calibrated, or any decision based on them was adequate.
"""
import json
from collections.abc import Iterable

from evidence_bridge.bridge.provenance import apply_provenance

SOURCE_SYSTEM = "PILOT_EDGE_SYNTHETIC"
SCHEMA_VERSION = "1.0.0"


def _event(row: dict, operation_scope_id: str) -> dict:
    reading = json.loads(row["payload"])
    if not isinstance(reading, dict):
        raise ValueError(f"buffer row seq={row['seq']}: payload is not a JSON object")
    return {
        "event_id": "EVT-" + row["event_id"][:32],
        "event_type": "TELEMETRY_READING",
        "source_system": SOURCE_SYSTEM,
        "source_event_id": row["event_id"],
        "operation_scope_id": operation_scope_id,
        "device_id": reading["device_id"],
        "device_id_status": "PROVIDED",
        "metric": reading["metric"],
        "value": reading["value"],
        "unit": reading["unit"],
        "occurred_at": reading["occurred_at"],
        "occurred_at_status": "PROVIDED",
        "received_at": row["ts"],
        "received_at_status": "GENERATED_BY_BRIDGE",
        "sequence_number": row["seq"],
        "sequence_status": "GENERATED_BY_BRIDGE",
        "source_config_version": None,
        "ingestion_mode": "READ_ONLY",
        "schema_version": SCHEMA_VERSION,
        "qms_reference": None,
        "qms_reference_status": "NOT_AVAILABLE",
        "review_status": "PENDING",
    }


def buffer_rows_to_events(rows: Iterable[dict], *, operation_scope_id: str) -> list:
    """Chained, schema-shaped events in seq order. Raises ValueError on a row that cannot be exported."""
    if not isinstance(operation_scope_id, str) or not operation_scope_id:
        raise ValueError("operation_scope_id is required")
    events, previous = [], None
    for row in sorted(rows, key=lambda r: r["seq"]):
        stamped = apply_provenance(_event(row, operation_scope_id), previous)
        events.append(stamped)
        previous = stamped["payload_hash"]
    return events

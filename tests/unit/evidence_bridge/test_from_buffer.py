"""Adapter from gateway buffer rows to Evidence Bridge telemetry events."""
import json

import pytest

from evidence_bridge.bridge.from_buffer import SOURCE_SYSTEM, buffer_rows_to_events
from evidence_bridge.bridge.provenance import verify_event_hash
from evidence_bridge.bridge.validate import validate_telemetry_event

SCOPE = "PILOT-TEST-SCOPE"


def row(seq, value=21.0, event_id=None):
    payload = {
        "device_id": "sensor-temp-01", "metric": "temperature", "value": value, "unit": "degC",
        "occurred_at": f"2026-11-11T08:{seq:02d}:00+00:00",
    }
    return {
        "seq": seq,
        "event_id": event_id or f"{seq:064x}",
        "ts": f"2026-11-11T08:{seq:02d}:01+00:00",
        "topic": "castuo/pilot/zona1/sensors",
        "payload": json.dumps(payload),
    }


def test_every_event_is_schema_valid_hashed_and_read_only():
    events = buffer_rows_to_events([row(1), row(2), row(3)], operation_scope_id=SCOPE)
    assert len(events) == 3
    for event in events:
        assert validate_telemetry_event(event).valid
        assert verify_event_hash(event)
        assert event["ingestion_mode"] == "READ_ONLY"
        assert event["review_status"] == "PENDING"
        assert event["source_system"] == SOURCE_SYSTEM == "PILOT_EDGE_SYNTHETIC"
        assert event["operation_scope_id"] == SCOPE


def test_ids_link_back_to_the_buffer_and_are_deterministic():
    first = buffer_rows_to_events([row(1), row(2)], operation_scope_id=SCOPE)
    again = buffer_rows_to_events([row(1), row(2)], operation_scope_id=SCOPE)
    assert first == again
    assert first[0]["source_event_id"] == f"{1:064x}"
    assert first[0]["event_id"] == "EVT-" + f"{1:064x}"[:32]
    assert first[0]["sequence_number"] == 1
    assert first[0]["sequence_status"] == "GENERATED_BY_BRIDGE"


def test_the_hash_chain_follows_seq_order_whatever_the_input_order():
    events = buffer_rows_to_events([row(3), row(1), row(2)], operation_scope_id=SCOPE)
    assert [e["sequence_number"] for e in events] == [1, 2, 3]
    assert events[0]["previous_event_hash"] is None
    assert events[1]["previous_event_hash"] == events[0]["payload_hash"]
    assert events[2]["previous_event_hash"] == events[1]["payload_hash"]


def test_changing_one_reading_changes_its_hash_and_every_later_link():
    base = buffer_rows_to_events([row(1), row(2), row(3)], operation_scope_id=SCOPE)
    changed = buffer_rows_to_events([row(1), row(2, value=99.0), row(3)], operation_scope_id=SCOPE)
    assert base[0]["payload_hash"] == changed[0]["payload_hash"]
    assert base[1]["payload_hash"] != changed[1]["payload_hash"]
    assert base[2]["payload_hash"] != changed[2]["payload_hash"]


def test_no_rows_is_an_empty_list_not_an_error():
    assert buffer_rows_to_events([], operation_scope_id=SCOPE) == []


def test_a_row_whose_payload_is_not_a_json_object_is_refused():
    bad = row(1)
    bad["payload"] = "[1, 2]"
    with pytest.raises(ValueError):
        buffer_rows_to_events([bad], operation_scope_id=SCOPE)


def test_an_empty_scope_is_refused():
    with pytest.raises(ValueError):
        buffer_rows_to_events([row(1)], operation_scope_id="")

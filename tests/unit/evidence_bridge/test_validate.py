from evidence_bridge.bridge.validate import validate_telemetry_event

VALID_EVENT = {
    "event_id": "EVT-2026-TEST-001",
    "event_type": "TELEMETRY_READING",
    "source_system": "SYNTHETIC_CULTIVATION_SAAS",
    "source_event_id": "synthetic-alert-test-001",
    "operation_scope_id": "EB-POC-001",
    "device_id": "sensor-temp-99",
    "device_id_status": "PROVIDED",
    "metric": "temperature",
    "value": 21.0,
    "unit": "degC",
    "occurred_at": "2026-09-14T09:00:00Z",
    "occurred_at_status": "PROVIDED",
    "ingestion_mode": "READ_ONLY",
    "schema_version": "1.0.0",
    "review_status": "PENDING",
}


def test_valid_event_passes():
    result = validate_telemetry_event(VALID_EVENT)
    assert result.valid is True
    assert result.event == VALID_EVENT
    assert result.errors == []


def test_missing_required_field_fails():
    broken = dict(VALID_EVENT)
    del broken["unit"]
    result = validate_telemetry_event(broken)
    assert result.valid is False
    assert result.event is None
    assert result.errors


def test_unknown_provenance_value_fails():
    broken = dict(VALID_EVENT)
    broken["occurred_at_status"] = "REFERENCE_ONLY"
    result = validate_telemetry_event(broken)
    assert result.valid is False

import copy

from evidence_bridge.bridge.provenance import apply_provenance, verify_event_hash

BASE_EVENT = {
    "event_id": "EVT-2026-TEST-100",
    "source_system": "SYNTHETIC_CULTIVATION_SAAS",
    "source_event_id": "synthetic-alert-test-100",
    "operation_scope_id": "EB-POC-001",
    "metric": "temperature",
    "value": 21.0,
    "unit": "degC",
    "occurred_at": "2026-09-14T09:00:00Z",
    "ingestion_mode": "READ_ONLY",
    "schema_version": "1.0.0",
}


def test_apply_provenance_sets_hash_and_verifies():
    stamped = apply_provenance(BASE_EVENT)
    assert stamped["payload_hash"].startswith("sha256:")
    assert stamped["previous_event_hash"] is None
    assert verify_event_hash(stamped) is True


def test_tampering_after_stamping_fails_verification():
    stamped = apply_provenance(BASE_EVENT)
    tampered = copy.deepcopy(stamped)
    tampered["value"] = 99.9
    assert verify_event_hash(tampered) is False


def test_missing_hash_fails_verification():
    assert verify_event_hash(dict(BASE_EVENT)) is False


def test_chain_links_two_events():
    first = apply_provenance(BASE_EVENT)
    second_raw = dict(BASE_EVENT, event_id="EVT-2026-TEST-101", value=21.5)
    second = apply_provenance(second_raw, previous_event_hash=first["payload_hash"])

    assert second["previous_event_hash"] == first["payload_hash"]
    assert verify_event_hash(first) is True
    assert verify_event_hash(second) is True


def test_splicing_the_chain_breaks_downstream_verification():
    first = apply_provenance(BASE_EVENT)
    second_raw = dict(BASE_EVENT, event_id="EVT-2026-TEST-101", value=21.5)
    second = apply_provenance(second_raw, previous_event_hash=first["payload_hash"])

    spliced = dict(second, previous_event_hash="sha256:" + "0" * 64)
    assert verify_event_hash(spliced) is False

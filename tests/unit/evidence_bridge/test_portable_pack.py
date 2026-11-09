"""EB-POC-001 portable export/verify — synthetic, offline, no authorization."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from evidence_bridge.bridge.export_pack import export_pack
from evidence_bridge.bridge.verify_pack import verify_pack
from evidence_bridge.bridge.provenance import apply_provenance

SHA = "a" * 40
TIME = "2026-10-31T12:00:00Z"
SCOPE = "EB-POC-001"


def events():
    previous = None
    result = []
    for index in (1, 2, 3):
        raw = {
            "event_id": f"EVT-2026-{index:06d}",
            "event_type": "TELEMETRY_READING",
            "source_system": "SYNTHETIC_CULTIVATION_SAAS",
            "source_event_id": f"synthetic-{index}",
            "operation_scope_id": SCOPE,
            "device_id": "synthetic-device",
            "metric": "temperature",
            "value": 20.0 + index,
            "unit": "degC",
            "occurred_at": TIME,
            "ingestion_mode": "READ_ONLY",
            "schema_version": "1.0.0",
        }
        stamped = apply_provenance(raw, previous)
        result.append(stamped)
        previous = stamped["payload_hash"]
    return result


def export(tmp_path: Path, items=None):
    pack = tmp_path / "pack"
    export_pack(events() if items is None else items, pack,
                source_commit=SHA, generated_at=TIME, operation_scope_id=SCOPE)
    return pack


def test_clean_pack_verified_with_unchanged_source(tmp_path):
    pack = export(tmp_path)
    report = verify_pack(pack)
    assert report["status"] == "VALID_LOCAL_INTEGRITY_ONLY"
    assert report["events"] == 3
    assert report["promotion"] == "BLOCKED"
    assert report["independent_review"] == "PENDING"
    assert verify_pack(pack)["manifest_hash"] == report["manifest_hash"]


def test_identical_events_same_manifest(tmp_path):
    p1 = export(tmp_path / "one")
    p2 = export(tmp_path / "two")
    assert (p1 / "manifest.json").read_bytes() == (p2 / "manifest.json").read_bytes()
    assert (p1 / "events.jsonl").read_bytes() == (p2 / "events.jsonl").read_bytes()


def test_change_event_detected(tmp_path):
    pack = export(tmp_path)
    path = pack / "events.jsonl"
    path.write_bytes(path.read_bytes().replace(b"21.0", b"99.0"))
    assert verify_pack(pack)["status"] == "INVALID"


def test_change_manifest_detected(tmp_path):
    pack = export(tmp_path)
    path = pack / "manifest.json"
    data = json.loads(path.read_text())
    data["source_commit"] = "b" * 40
    path.write_text(json.dumps(data))
    assert verify_pack(pack)["status"] == "INVALID"


def test_duplicated_event_rejected(tmp_path):
    values = events()
    with pytest.raises(ValueError, match="duplicate"):
        export(tmp_path, values + [copy.deepcopy(values[1])])


def test_reordered_chain_rejected(tmp_path):
    values = events()
    with pytest.raises(ValueError, match="predecessor"):
        export(tmp_path, [values[1], values[0], values[2]])


def test_cross_scope_rejected(tmp_path):
    values = events()
    values[0]["operation_scope_id"] = "OTHER"
    with pytest.raises(ValueError, match="cross-scope"):
        export(tmp_path, values)


def test_bad_source_sha_and_time_rejected(tmp_path):
    with pytest.raises(ValueError, match="source_commit"):
        export_pack(events(), tmp_path / "bad", source_commit="HEAD",
                    generated_at=TIME, operation_scope_id=SCOPE)
    with pytest.raises(ValueError, match="generated_at"):
        export_pack(events(), tmp_path / "bad", source_commit=SHA,
                    generated_at="2026-10-31T12:00:00", operation_scope_id=SCOPE)


def test_no_overwrite(tmp_path):
    pack = export(tmp_path)
    with pytest.raises(FileExistsError):
        export_pack(events(), pack, source_commit=SHA, generated_at=TIME,
                    operation_scope_id=SCOPE)


def test_missing_pack_denied(tmp_path):
    assert verify_pack(tmp_path / "missing")["status"] == "INVALID"

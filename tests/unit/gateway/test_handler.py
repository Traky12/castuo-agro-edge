"""Inbound validation and de-duplication in the MQTT gateway handler.

Every rejection is returned with a reason (never swallowed) and leaves the buffer
untouched. Nothing here touches a network or a broker.
"""
import json
import sqlite3
from datetime import datetime, timezone

import pytest

from gateway.mqtt.db import BufferDB
from gateway.mqtt.handler import Decision, process_message

TOPIC = "castuo/pilot/zona1/sensors"
NOW = datetime(2026, 11, 11, 8, 0, tzinfo=timezone.utc)


def reading(**overrides):
    body = {
        "device_id": "sensor-temp-01",
        "metric": "temperature",
        "value": 21.4,
        "unit": "degC",
        "occurred_at": "2026-11-11T07:55:00+00:00",
    }
    body.update(overrides)
    return body


@pytest.fixture
def db(tmp_path):
    database = BufferDB(tmp_path / "edge.db")
    yield database
    database.close()


def test_valid_reading_is_accepted_and_buffered(db):
    decision = process_message(TOPIC, json.dumps(reading()), db, now=NOW)
    assert decision == Decision(True, "accepted")
    assert db.stats() == {"pending": 1, "total": 1}
    stored = json.loads(db.pending(1)[0]["payload"])
    assert stored == reading()


def test_bytes_payload_is_accepted_like_text(db):
    decision = process_message(TOPIC, json.dumps(reading()).encode("utf-8"), db, now=NOW)
    assert decision.accepted


@pytest.mark.parametrize("raw, reason", [
    ('{"device_id": "sensor-temp-01", "metric": ', "malformed_json"),
    (b"\xff\xfe not utf-8", "malformed_json"),
    ("[1, 2, 3]", "not_an_object"),
    ("42", "not_an_object"),
    (json.dumps(reading(device_id="")), "missing_device_id"),
    (json.dumps({k: v for k, v in reading().items() if k != "device_id"}), "missing_device_id"),
    (json.dumps(reading(metric="soil_salinity_index")), "unknown_metric"),
    (json.dumps(reading(unit="kelvin")), "unknown_unit"),
    (json.dumps(reading(unit="pct")), "unknown_unit"),            # right unit for another metric
    (json.dumps(reading(value="21.4")), "value_not_numeric"),
    (json.dumps(reading(value=True)), "value_not_numeric"),
    (json.dumps(reading(value=None)), "value_not_numeric"),
    (json.dumps(reading()).replace("21.4", "NaN"), "non_finite_value"),
    (json.dumps(reading()).replace("21.4", "Infinity"), "non_finite_value"),
    (json.dumps(reading(occurred_at="2026-11-11T07:55:00")), "occurred_at_missing_timezone"),
    (json.dumps(reading(occurred_at="yesterday")), "occurred_at_invalid"),
    (json.dumps(reading(occurred_at=None)), "occurred_at_invalid"),
    (json.dumps(reading(set_valve="on")), "unexpected_fields"),     # a command smuggled in a reading
])
def test_invalid_reading_is_rejected_with_a_reason_and_not_buffered(db, raw, reason):
    decision = process_message(TOPIC, raw, db, now=NOW)
    assert decision == Decision(False, reason)
    assert db.stats() == {"pending": 0, "total": 0}


def test_redelivered_reading_is_rejected_as_duplicate(db):
    raw = json.dumps(reading())
    assert process_message(TOPIC, raw, db, now=NOW).accepted
    again = process_message(TOPIC, raw, db, now=datetime(2026, 11, 11, 8, 0, 9, tzinfo=timezone.utc))
    assert again == Decision(False, "duplicate_source_key")
    assert db.stats() == {"pending": 1, "total": 1}


def test_duplicate_is_still_detected_after_restart_and_after_sync(tmp_path):
    path = tmp_path / "edge.db"
    raw = json.dumps(reading())
    first = BufferDB(path)
    assert process_message(TOPIC, raw, first, now=NOW).accepted
    first.mark_synced(first.pending(1)[0]["id"])      # already delivered to the core
    first.close()

    second = BufferDB(path)                           # process restart
    assert process_message(TOPIC, raw, second, now=NOW) == Decision(False, "duplicate_source_key")
    assert second.stats()["total"] == 1
    second.close()


def test_same_instant_different_metric_or_device_is_not_a_duplicate(db):
    assert process_message(TOPIC, json.dumps(reading()), db, now=NOW).accepted
    assert process_message(TOPIC, json.dumps(reading(device_id="sensor-temp-02")), db, now=NOW).accepted
    assert process_message(TOPIC, json.dumps(reading(metric="humidity", unit="pct", value=55.0)), db, now=NOW).accepted
    assert db.stats()["total"] == 3


@pytest.mark.parametrize("topic", [
    "castuo/zona1/commands/riego/set",
    "castuo/commands/zona1/riego",
    "castuo/actuators/zona1/riego/on",
    "castuo/invernadero/zona1/Actuators/riego/ON",
    "castuo/zona1/riego/set",
    "castuo/zona1/Set",
])
def test_actuation_topics_are_rejected_even_with_a_valid_reading(db, topic):
    decision = process_message(topic, json.dumps(reading()), db, now=NOW)
    assert decision == Decision(False, "actuation_topic_rejected")
    assert db.stats() == {"pending": 0, "total": 0}


def test_buffer_written_before_source_key_existed_is_migrated_and_keeps_its_rows(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE buffer (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, topic TEXT NOT NULL,"
                 " payload TEXT NOT NULL, synced INTEGER NOT NULL DEFAULT 0, synced_at TEXT)")
    conn.execute("INSERT INTO buffer (ts, topic, payload) VALUES ('2026-10-10T00:00:00+00:00', ?, '{\"value\": 7}')", (TOPIC,))
    conn.commit()
    conn.close()

    database = BufferDB(path)
    assert database.stats() == {"pending": 1, "total": 1}
    assert process_message(TOPIC, json.dumps(reading()), database, now=NOW).accepted
    assert process_message(TOPIC, json.dumps(reading()), database, now=NOW).reason == "duplicate_source_key"
    database.close()


def test_enqueue_without_source_key_keeps_the_legacy_behaviour(db):
    db.enqueue(TOPIC, {"value": 1})
    db.enqueue(TOPIC, {"value": 1})        # legacy callers get no de-duplication
    assert db.stats()["total"] == 2

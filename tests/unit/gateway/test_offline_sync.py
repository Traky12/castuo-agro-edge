"""T-SYNC-01..03: offline buffering and ordered, at-least-once replay.

These tests model the current canonical API contract, not an imagined server-side
idempotency layer. The edge reuses a stable message_id after retries; when an ACK
is lost after the API accepts a request, the real API may persist a duplicate until
durable API-side deduplication is implemented and verified.
"""
import json
import logging
import random
import sqlite3
from collections import Counter

import pytest
import requests

from gateway.mqtt import sync as sync_module
from gateway.mqtt.db import BufferDB
from gateway.mqtt.sync import SyncWorker, _build_ingest_payload

TOPIC = "castuo/invernadero/zona1/sensores"
N = 50


class FakeCore:
    """Small fake for the actual endpoint contract; it intentionally does not deduplicate."""

    def __init__(self):
        self.online = True
        self.events = []          # every payload accepted by the fake API
        self.deliveries = []      # every POST that reached the fake API
        self.lose_ack_times = 0   # store the event, then fail before client sees 2xx
        self.fail_with_500 = 0

    def post(self, url, json=None, headers=None, timeout=None):
        if not self.online:
            raise requests.ConnectionError("network down")
        if self.fail_with_500:
            self.fail_with_500 -= 1
            return _Response(500)

        assert url == "https://core.invalid/api/v1/iot/data"
        assert headers["X-API-Key"] == "test-key"
        assert "Idempotency-Key" not in headers  # not supported by the current API
        body = json
        assert body["schema_version"] == "iot.v1"
        assert body["message_id"]
        assert "soil_1" in body
        self.deliveries.append(body)
        self.events.append(body)  # the current API may store a retry as a duplicate

        if self.lose_ack_times:
            self.lose_ack_times -= 1
            raise requests.ConnectionError("connection lost after the API accepted the event")
        return _Response(201)


class _Response:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.fixture
def core(monkeypatch):
    fake = FakeCore()
    monkeypatch.setattr(sync_module.requests, "post", fake.post)
    return fake


def _worker(db):
    return SyncWorker(db, "https://core.invalid", "test-key", "edge-01", batch_size=7)


def _drain(worker, db, rounds=200):
    for _ in range(rounds):
        if db.stats()["pending"] == 0:
            return
        worker.run_once()
    raise AssertionError(f"still pending after {rounds} rounds: {db.stats()}")


def _received_values(core):
    ordered = sorted(core.events, key=lambda event: event["metadata"]["edge_seq"])
    return [event["soil_1"] for event in ordered]


def test_tsync01_offline_restart_then_reconnect_delivers_all_events_in_order(tmp_path, core):
    path = tmp_path / "edge.db"
    db = BufferDB(path)
    core.online = False
    for i in range(N):
        db.enqueue(TOPIC, {"soil_1": i})
    _worker(db).run_once()                     # offline attempt: nothing is dropped
    assert db.stats() == {"pending": N, "total": N}
    db.close()

    db = BufferDB(path)                        # process restart
    core.online = True
    _drain(_worker(db), db)

    assert len(core.events) == N
    assert _received_values(core) == list(range(N))
    assert [
        event["metadata"]["edge_seq"]
        for event in sorted(core.events, key=lambda event: event["metadata"]["edge_seq"])
    ] == list(range(1, N + 1))


def test_tsync02_ack_lost_reuses_stable_message_id_but_does_not_claim_server_dedup(tmp_path, core):
    db = BufferDB(tmp_path / "edge.db")
    for i in range(N):
        db.enqueue(TOPIC, {"soil_1": i})
    core.lose_ack_times = 3
    _drain(_worker(db), db)

    assert len(core.events) == N + 3            # accepted retries can be duplicate writes
    message_counts = Counter(event["message_id"] for event in core.events)
    assert len(message_counts) == N             # stable identity survives all retries
    repeated_id, repeated_count = max(message_counts.items(), key=lambda item: item[1])
    assert repeated_count == 4                  # three lost ACKs + one acknowledged retry
    repeated_events = [e for e in core.events if e["message_id"] == repeated_id]
    assert all(event == repeated_events[0] for event in repeated_events)
    assert _received_values(core) == [0, 0, 0, 0, *range(1, N)]


def test_tsync03_interrupted_network_and_500_lose_nothing_and_record_failures(tmp_path, core, caplog):
    db = BufferDB(tmp_path / "edge.db")
    for i in range(N):
        db.enqueue(TOPIC, {"soil_1": i})
    worker = _worker(db)
    rng = random.Random(20261010)
    caplog.set_level(logging.WARNING, logger="castuo.edge.sync")
    for _ in range(400):
        if db.stats()["pending"] == 0:
            break
        core.online = rng.random() > 0.4
        core.fail_with_500 = 1 if rng.random() < 0.2 else 0
        worker.run_once()
    core.online, core.fail_with_500 = True, 0
    _drain(worker, db)

    assert len(core.events) == N
    assert _received_values(core) == list(range(N))
    failures = db.failure_log()
    assert failures, "failed attempts must be recorded, not swallowed"
    assert all(f["last_error"] for f in failures)
    assert any("network down" in r.getMessage() or "HTTP 500" in r.getMessage() for r in caplog.records)


def test_event_and_message_ids_are_stable_across_restart(tmp_path):
    path = tmp_path / "edge.db"
    db = BufferDB(path)
    db.enqueue(TOPIC, {"soil_1": 1})
    row = db.pending(1)[0]
    first_event_id = row["event_id"]
    first_message_id = _build_ingest_payload(row, "edge-01")["message_id"]
    db.close()

    restarted = BufferDB(path)
    row_after_restart = restarted.pending(1)[0]
    assert row_after_restart["event_id"] == first_event_id
    assert _build_ingest_payload(row_after_restart, "edge-01")["message_id"] == first_message_id
    assert len(first_event_id) == 64


def test_existing_buffer_without_event_id_is_migrated(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE buffer (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, topic TEXT NOT NULL,"
        " payload TEXT NOT NULL, synced INTEGER NOT NULL DEFAULT 0, synced_at TEXT)"
    )
    conn.execute(
        "INSERT INTO buffer (ts, topic, payload) VALUES ('2026-10-10T00:00:00+00:00', ?, '{\"soil_1\": 7}')",
        (TOPIC,),
    )
    conn.commit()
    conn.close()

    row = BufferDB(path).pending(1)[0]
    assert len(row["event_id"]) == 64
    assert row["seq"] == 1


def test_payload_without_canonical_sensor_reading_is_not_sent_or_dropped(tmp_path, core):
    db = BufferDB(tmp_path / "edge.db")
    db.enqueue(TOPIC, {"value": 7})
    worker = _worker(db)

    assert worker.run_once() is False
    assert core.deliveries == []
    assert db.stats() == {"pending": 1, "total": 1}
    assert "no recognized sensor readings" in db.failure_log()[0]["last_error"]

"""T-SYNC-01..03: offline buffering and resend on the edge gateway.

The core is simulated in memory and `requests.post` is replaced, so these tests make
no network calls. The fake core deduplicates by event_id, as the real core must; what
these tests prove is the edge side of the contract: every event keeps one stable id,
nothing is lost, order is kept and every failure is recorded.
"""
import json
import logging
import random
import sqlite3

import pytest
import requests

from gateway.mqtt import sync as sync_module
from gateway.mqtt.db import BufferDB
from gateway.mqtt.sync import SyncWorker

TOPIC = "castuo/invernadero/zona1/sensores"
N = 50


class FakeCore:
    """In-memory core that stores events by event_id and can misbehave on purpose."""

    def __init__(self):
        self.online = True
        self.events = {}          # event_id -> body
        self.deliveries = []      # every POST that reached the core
        self.lose_ack_times = 0   # store the event, then fail before the client sees 2xx
        self.fail_with_500 = 0

    def post(self, url, json=None, headers=None, timeout=None):
        if not self.online:
            raise requests.ConnectionError("network down")
        if self.fail_with_500:
            self.fail_with_500 -= 1
            return _Response(500)
        body = json
        assert headers["Idempotency-Key"] == body["event_id"]
        self.deliveries.append(body)
        stable = {k: v for k, v in body.items() if k != "gateway_ts"}
        previous = self.events.get(body["event_id"])
        assert previous is None or {k: v for k, v in previous.items() if k != "gateway_ts"} == stable, "same event_id with a different event"
        self.events[body["event_id"]] = body
        if self.lose_ack_times:
            self.lose_ack_times -= 1
            raise requests.ConnectionError("connection lost after the core stored the event")
        return _Response(201 if previous is None else 200)


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
    by_seq = sorted(core.events.values(), key=lambda e: e["seq"])
    return [json.loads(e["payload"])["value"] for e in by_seq]


def test_tsync01_offline_restart_then_reconnect_delivers_exactly_n(tmp_path, core):
    path = tmp_path / "edge.db"
    db = BufferDB(path)
    core.online = False
    for i in range(N):
        db.enqueue(TOPIC, {"value": i})
    _worker(db).run_once()                     # offline attempt: nothing sent, nothing lost
    assert db.stats() == {"pending": N, "total": N}
    db.close()

    db = BufferDB(path)                        # process restart
    core.online = True
    _drain(_worker(db), db)

    assert len(core.events) == N
    assert _received_values(core) == list(range(N))
    assert [e["seq"] for e in sorted(core.events.values(), key=lambda e: e["seq"])] == list(range(1, N + 1))


def test_tsync02_ack_lost_after_core_stored_resends_same_event_id(tmp_path, core):
    db = BufferDB(tmp_path / "edge.db")
    for i in range(N):
        db.enqueue(TOPIC, {"value": i})
    core.lose_ack_times = 3
    _drain(_worker(db), db)

    assert len(core.events) == N               # exactly N unique events in the core
    assert len(core.deliveries) == N + 3       # three resends, each with the same id and body
    assert _received_values(core) == list(range(N))


def test_tsync03_intermittent_network_and_500_lose_nothing_and_record_failures(tmp_path, core, caplog):
    db = BufferDB(tmp_path / "edge.db")
    for i in range(N):
        db.enqueue(TOPIC, {"value": i})
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


def test_event_id_is_stable_across_restart(tmp_path):
    path = tmp_path / "edge.db"
    db = BufferDB(path)
    db.enqueue(TOPIC, {"value": 1})
    first = db.pending(1)[0]["event_id"]
    db.close()
    assert BufferDB(path).pending(1)[0]["event_id"] == first


def test_existing_buffer_without_event_id_is_migrated(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE buffer (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, topic TEXT NOT NULL,"
                 " payload TEXT NOT NULL, synced INTEGER NOT NULL DEFAULT 0, synced_at TEXT)")
    conn.execute("INSERT INTO buffer (ts, topic, payload) VALUES ('2026-10-10T00:00:00+00:00', ?, '{\"value\": 7}')", (TOPIC,))
    conn.commit()
    conn.close()

    row = BufferDB(path).pending(1)[0]
    assert len(row["event_id"]) == 64
    assert row["seq"] == 1

"""Minimal demonstrable pilot circuit, end to end, with no network and no hardware.

    ingest -> validate -> buffer -> network cut -> restart -> idempotent sync -> evidence pack -> verify

WHAT THIS PROVES (synthetic data, local, deterministic):
  * only valid readings are buffered; every rejection is counted with its reason;
  * a redelivered reading and a command topic never reach the buffer;
  * readings survive a network cut and a restart (clean close, and a process that dies
    without closing the database) with stable event_id and seq;
  * after reconnection with a lost ACK and an HTTP 500 the core holds exactly N unique
    events, in order, none lost;
  * the exported pack passes the independent local verifier, matches the events the
    core received, and the verifier fails closed when the pack is altered - including by
    someone who recomputes the manifest hashes.

WHAT THIS DOES NOT PROVE (and must not be cited as proof of):
  * data quality, sensor calibration or an adequate irrigation decision - document
    integrity (hash chain) is not the same thing as correct readings;
  * the real core: it is a simulation in memory (CORE-006 is not exercised);
  * real MQTT, a broker, TLS/authentication, or any hardware or field behaviour;
  * a signature: VALID_LOCAL_INTEGRITY_ONLY is a local hash check, promotion stays BLOCKED
    and independent review stays PENDING.

Maturity this supports: TESTED in a synthetic, local environment. Nothing more.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from evidence_bridge.bridge.export_pack import canonical, digest, export_pack
from evidence_bridge.bridge.from_buffer import buffer_rows_to_events
from evidence_bridge.bridge.verify_pack import verify_pack
from gateway.mqtt import sync as sync_module
from gateway.mqtt.db import BufferDB
from gateway.mqtt.handler import Decision, process_message
from gateway.mqtt.sync import SyncWorker
from tests.support.fake_core import FakeCore

ROOT = Path(__file__).resolve().parents[3]
SCOPE = "PILOT-E2E-SYNTHETIC"
SENSORS = "castuo/pilot/zona1/sensors"
COMMANDS = "castuo/pilot/zona1/commands/riego/set"
BASE = datetime(2026, 11, 11, 8, 0, tzinfo=timezone.utc)
N = 20
SYNTHETIC_COMMIT = "0" * 40          # placeholder: the release step stamps the real commit
GENERATED_AT = "2026-11-11T09:00:00+00:00"


def reading(i):
    return {
        "device_id": "sensor-temp-01", "metric": "temperature", "value": round(20.0 + i * 0.1, 1),
        "unit": "degC", "occurred_at": (BASE + timedelta(minutes=5 * i)).isoformat(),
    }


def script():
    """(topic, raw payload) in arrival order: N valid, four invalid, one redelivery, one command."""
    valid = [json.dumps(reading(i)) for i in range(N)]
    invalid = [
        '{"device_id": "sensor-temp-01", "metric": ',                                    # malformed_json
        json.dumps(reading(40)).replace(str(reading(40)["value"]), "NaN"),                # non_finite_value
        json.dumps({**reading(41), "unit": "furlongs"}),                                  # unknown_unit
        json.dumps({**reading(42), "occurred_at": "2026-11-11T12:00:00"}),                # occurred_at_missing_timezone
    ]
    return (
        [(SENSORS, raw) for raw in valid]
        + [(SENSORS, raw) for raw in invalid]
        + [(SENSORS, valid[3])]                                                           # QoS1-style redelivery
        + [(COMMANDS, json.dumps(reading(50)))]                                           # actuation topic
    )


def at(index):
    return BASE + timedelta(seconds=index)


EXPECTED_REJECTIONS = {
    "malformed_json": 1, "non_finite_value": 1, "unknown_unit": 1,
    "occurred_at_missing_timezone": 1, "duplicate_source_key": 1, "actuation_topic_rejected": 1,
}


@pytest.fixture
def no_network(monkeypatch):
    """Any attempt to open a socket fails the test: 'no network' is enforced, not assumed."""
    attempts = []

    def refuse(*args, **kwargs):
        attempts.append(args)
        raise OSError("network access is blocked by the test")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    yield attempts


@pytest.fixture
def core(monkeypatch):
    fake = FakeCore()
    monkeypatch.setattr(sync_module.requests, "post", fake.post)
    return fake


def worker(db):
    return SyncWorker(db, "https://core.invalid", "test-key", "edge-01", batch_size=7)


def drain(sync_worker, db, rounds=200):
    for _ in range(rounds):
        if db.stats()["pending"] == 0:
            return
        sync_worker.run_once()
    raise AssertionError(f"still pending after {rounds} rounds: {db.stats()}")


CHILD = """
import json, os, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from gateway.mqtt.db import BufferDB
from gateway.mqtt.handler import process_message

db = BufferDB(Path(sys.argv[2]))
out = []
for topic, raw, now in json.load(open(sys.argv[3], encoding="utf-8")):
    decision = process_message(topic, raw, db, now=datetime.fromisoformat(now))
    out.append([decision.accepted, decision.reason])
sys.stdout.write(json.dumps(out))
sys.stdout.flush()
os._exit(0)   # the process dies here WITHOUT closing the database: no checkpoint, no clean shutdown
"""


def ingest_in_process(db_path, messages):
    db = BufferDB(db_path)
    decisions = [process_message(t, raw, db, now=at(i)) for i, (t, raw) in enumerate(messages)]
    db.close()
    return decisions


def ingest_in_a_process_that_dies(db_path, messages, workdir):
    plan = workdir / "plan.json"
    plan.write_text(json.dumps([[t, raw, at(i).isoformat()] for i, (t, raw) in enumerate(messages)]), encoding="utf-8")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    done = subprocess.run([sys.executable, "-c", CHILD, str(ROOT), str(db_path), str(plan)],
                          cwd=workdir, env=env, capture_output=True, text=True, timeout=120, check=False)
    assert done.returncode == 0, done.stderr
    return [Decision(accepted, reason) for accepted, reason in json.loads(done.stdout)]


@pytest.mark.parametrize("restart", ["clean_close", "process_dies_without_close"])
def test_pilot_circuit_end_to_end(tmp_path, no_network, core, restart):
    db_path = tmp_path / "edge" / "buffer.db"
    messages = script()

    # 1. Ingestion (and, in the hard variant, the process dies right after the last message).
    if restart == "clean_close":
        decisions = ingest_in_process(db_path, messages)
    else:
        decisions = ingest_in_a_process_that_dies(db_path, messages, tmp_path)
    assert sum(d.accepted for d in decisions) == N
    assert Counter(d.reason for d in decisions if not d.accepted) == EXPECTED_REJECTIONS

    # 2. The database is reopened: every accepted reading is there, nothing else.
    db = BufferDB(db_path)
    assert db.stats() == {"pending": N, "total": N}
    first_ids = [(r["seq"], r["event_id"]) for r in db.pending(1000)]
    assert [seq for seq, _ in first_ids] == list(range(1, N + 1))
    assert len({event_id for _, event_id in first_ids}) == N

    # 3. Network cut: nothing is sent, nothing is lost, the failure is recorded.
    core.online = False
    worker(db).run_once()
    assert core.events == {} and core.deliveries == []
    assert db.stats() == {"pending": N, "total": N}
    failures = db.failure_log()
    assert failures and all("network down" in f["last_error"] for f in failures)

    # 4. Restart with a backlog: identifiers are stable.
    db.close()
    db = BufferDB(db_path)
    assert [(r["seq"], r["event_id"]) for r in db.pending(1000)] == first_ids

    # 5. Reconnection with a lost ACK (x3) and an HTTP 500: the core ends with exactly N unique events.
    core.online = True
    core.lose_ack_times = 3
    core.fail_with_500 = 1
    drain(worker(db), db)
    ordered = sorted(core.events.values(), key=lambda e: e["seq"])
    assert len(core.events) == N
    assert len(core.deliveries) == N + 3          # three resends carrying the same id and body; the 500 never arrived
    assert [e["seq"] for e in ordered] == list(range(1, N + 1))
    assert db.stats()["pending"] == 0
    first_row = db.failure_log()[0]
    assert (first_row["seq"], first_row["attempts"]) == (1, 5)   # 1 network cut + 1 HTTP 500 + 3 lost ACKs, all recorded
    assert first_row["last_error"]

    # 6. Evidence pack: exported from what was actually synced, verified independently.
    events = buffer_rows_to_events(db.synced_rows(), operation_scope_id=SCOPE)
    assert len(events) == N
    pack = tmp_path / "pack"
    exported = export_pack(events, pack, source_commit=SYNTHETIC_COMMIT, generated_at=GENERATED_AT,
                           operation_scope_id=SCOPE)
    verdict = verify_pack(pack)
    assert verdict["status"] == "VALID_LOCAL_INTEGRITY_ONLY"
    assert verdict["events"] == N
    assert verdict["promotion"] == "BLOCKED" and verdict["independent_review"] == "PENDING"
    in_pack = [json.loads(line) for line in (pack / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {e["source_event_id"] for e in in_pack} == set(core.events), "pack must reconcile with what the core received"
    assert [e["sequence_number"] for e in in_pack] == list(range(1, N + 1))
    db.close()

    # 7. Declared limits, as assertions: no state above 'local integrity' is claimed anywhere.
    claimed = json.dumps([exported, verdict])
    for word in ("VALIDATED", "SIGNED", "CERTIFIED", "OPERATIONAL"):
        assert word not in claimed
    assert no_network == [], "the test attempted network access"


def make_pack(tmp_path, core):
    tmp_path.mkdir(parents=True, exist_ok=True)
    db = BufferDB(tmp_path / "edge" / "buffer.db")
    for i in range(N):
        assert process_message(SENSORS, json.dumps(reading(i)), db, now=at(i)).accepted
    drain(worker(db), db)
    events = buffer_rows_to_events(db.synced_rows(), operation_scope_id=SCOPE)
    db.close()
    pack = tmp_path / "pack"
    export_pack(events, pack, source_commit=SYNTHETIC_COMMIT, generated_at=GENERATED_AT, operation_scope_id=SCOPE)
    return pack


def tamper(pack, how, rehash):
    lines = (pack / "events.jsonl").read_bytes().splitlines(keepends=True)
    if how == "value_changed":
        event = json.loads(lines[4])
        event["value"] = event["value"] + 1.0
        lines[4] = canonical(event) + b"\n"
    elif how == "event_deleted":
        del lines[7]
    elif how == "events_reordered":
        lines[2], lines[3] = lines[3], lines[2]
    raw = b"".join(lines)
    (pack / "events.jsonl").write_bytes(raw)
    if rehash:      # the stronger attacker also recomputes the file digest and the manifest hash
        manifest = json.loads((pack / "manifest.json").read_bytes())
        manifest.pop("manifest_hash")
        manifest["files"] = [{"path": "events.jsonl", "sha256": digest(raw)}]
        manifest["manifest_hash"] = digest(canonical(manifest))
        (pack / "manifest.json").write_bytes(canonical(manifest) + b"\n")


@pytest.mark.parametrize("rehash", [False, True], ids=["naive", "manifest_rehashed"])
@pytest.mark.parametrize("how", ["value_changed", "event_deleted", "events_reordered"])
def test_verifier_fails_closed_when_the_pack_is_altered(tmp_path, no_network, core, how, rehash):
    pack = make_pack(tmp_path, core)
    assert verify_pack(pack)["status"] == "VALID_LOCAL_INTEGRITY_ONLY", "control: the untouched pack must verify"
    altered = tmp_path / "altered"
    shutil.copytree(pack, altered)
    tamper(altered, how, rehash)
    verdict = verify_pack(altered)
    assert verdict["status"] == "INVALID", (how, rehash, verdict)
    assert verdict["promotion"] == "BLOCKED"
    assert no_network == []


def test_exported_pack_is_reproducible_byte_for_byte(tmp_path, no_network, core):
    """Same synthetic input and fixed clock -> identical events.jsonl and manifest hash, in any directory."""
    first = make_pack(tmp_path / "a", core)
    core.events.clear()
    core.deliveries.clear()
    second = make_pack(tmp_path / "b", core)
    assert (first / "events.jsonl").read_bytes() == (second / "events.jsonl").read_bytes()
    assert verify_pack(first)["manifest_hash"] == verify_pack(second)["manifest_hash"]
    assert no_network == []


def test_buffer_keeps_wal_and_full_synchronous_settings(tmp_path):
    """Configuration guard, NOT a power-loss test: killing a process (as the E2E does) cannot show whether
    fsync is on, because the OS keeps what the process already wrote. Only the setting can be watched here;
    surviving real power loss needs a hardware test."""
    db = BufferDB(tmp_path / "edge.db")
    assert db._conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    assert db._conn.execute("PRAGMA synchronous").fetchone()[0] == 2     # 2 = FULL
    db.close()

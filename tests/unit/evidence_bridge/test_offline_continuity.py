import sqlite3

import pytest

from evidence_bridge.offline import queue_adapter

EVENT = {
    "event_id": "EVT-2026-TEST-200",
    "source_system": "SYNTHETIC_CULTIVATION_SAAS",
    "metric": "temperature",
    "value": 21.0,
}


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    queue_adapter.init_queue(connection)
    yield connection
    connection.close()


def test_enqueue_then_pending_lists_the_event(conn):
    queue_adapter.enqueue(EVENT, "2026-09-14T09:00:02Z", conn=conn)
    pending = queue_adapter.pending(conn=conn)
    assert len(pending) == 1
    assert pending[0]["event_id"] == EVENT["event_id"]


def test_retry_after_reconnection_is_idempotent(conn):
    queue_adapter.enqueue(EVENT, "2026-09-14T09:00:02Z", conn=conn)
    queue_adapter.enqueue(EVENT, "2026-09-14T09:00:02Z", conn=conn)
    pending = queue_adapter.pending(conn=conn)
    assert len(pending) == 1


def test_mark_synced_removes_event_from_pending(conn):
    queue_adapter.enqueue(EVENT, "2026-09-14T09:00:02Z", conn=conn)
    queue_adapter.mark_synced(EVENT["event_id"], conn=conn)
    assert queue_adapter.pending(conn=conn) == []

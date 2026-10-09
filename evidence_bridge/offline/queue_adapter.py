"""Offline continuity queue for Evidence Bridge events.

Shares the SQLite file used by gateway/buffering/store.py (settings.buffer_sqlite_path)
but owns a separate table (evidence_bridge_events) — it never reads or writes
telemetry_queue, so it cannot collide with the existing buffering path or with
gateway/mqtt's separate BufferDB/SyncWorker daemon.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

from gateway.config import settings

_TABLE = "evidence_bridge_events"


def _connect() -> sqlite3.Connection:
    path = Path(settings.buffer_sqlite_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_queue(conn: Optional[sqlite3.Connection] = None) -> None:
    owns_conn = conn is None
    conn = conn or _connect()
    try:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                event_json TEXT NOT NULL,
                ingested_at TEXT NOT NULL,
                synced INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        if owns_conn:
            conn.close()


def enqueue(event: dict, ingested_at: str, conn: Optional[sqlite3.Connection] = None) -> None:
    """Idempotent: re-enqueuing an event_id already present is a no-op, so a retry after
    reconnection never duplicates an event that was queued before the connection dropped."""
    owns_conn = conn is None
    conn = conn or _connect()
    try:
        init_queue(conn)
        conn.execute(
            f"INSERT OR IGNORE INTO {_TABLE} (event_id, event_json, ingested_at, synced) VALUES (?, ?, ?, 0)",
            (event["event_id"], json.dumps(event, sort_keys=True, default=str), ingested_at),
        )
        conn.commit()
    finally:
        if owns_conn:
            conn.close()


def pending(conn: Optional[sqlite3.Connection] = None, limit: int = 100) -> list:
    owns_conn = conn is None
    conn = conn or _connect()
    try:
        init_queue(conn)
        rows = conn.execute(
            f"SELECT event_id, event_json, ingested_at FROM {_TABLE} WHERE synced=0 ORDER BY id ASC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        if owns_conn:
            conn.close()


def mark_synced(event_id: str, conn: Optional[sqlite3.Connection] = None) -> None:
    owns_conn = conn is None
    conn = conn or _connect()
    try:
        conn.execute(f"UPDATE {_TABLE} SET synced=1 WHERE event_id=?", (event_id,))
        conn.commit()
    finally:
        if owns_conn:
            conn.close()

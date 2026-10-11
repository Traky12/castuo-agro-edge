import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path


def _event_id(seq: int, ts: str, topic: str, payload: str) -> str:
    """Stable id fixed at enqueue time, so every resend of an event carries the same id."""
    return hashlib.sha256(f"{seq}|{ts}|{topic}|{payload}".encode("utf-8")).hexdigest()


class BufferDB:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        # Survive power loss: WAL journal, fsync on every commit.
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=FULL")
        self._init()

    def _init(self):
        with self._lock:
            self._conn.execute("""
            CREATE TABLE IF NOT EXISTS buffer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                synced INTEGER NOT NULL DEFAULT 0,
                synced_at TEXT
            )
            """)
            columns = {row["name"] for row in self._conn.execute("PRAGMA table_info(buffer)")}
            for name, ddl in (("seq", "INTEGER"), ("event_id", "TEXT"), ("attempts", "INTEGER NOT NULL DEFAULT 0"), ("last_error", "TEXT")):
                if name not in columns:
                    self._conn.execute(f"ALTER TABLE buffer ADD COLUMN {name} {ddl}")
            # Buffers written before event ids existed: number them in arrival order.
            for row in self._conn.execute("SELECT id, ts, topic, payload FROM buffer WHERE event_id IS NULL ORDER BY id").fetchall():
                self._conn.execute("UPDATE buffer SET seq=?, event_id=? WHERE id=?",
                                   (row["id"], _event_id(row["id"], row["ts"], row["topic"], row["payload"]), row["id"]))
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_buffer_synced_id ON buffer(synced, id)")
            self._conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_buffer_event_id ON buffer(event_id)")
            self._conn.commit()

    def enqueue(self, topic: str, payload: dict):
        with self._lock:
            ts = datetime.now(timezone.utc).isoformat()
            body = json.dumps(payload, ensure_ascii=False)
            seq = self._conn.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM buffer").fetchone()[0]
            self._conn.execute(
                "INSERT INTO buffer (ts, topic, payload, synced, seq, event_id) VALUES (?, ?, ?, 0, ?, ?)",
                (ts, topic, body, seq, _event_id(seq, ts, topic, body))
            )
            self._conn.commit()

    def pending(self, limit: int = 100):
        with self._lock:
            cur = self._conn.execute(
                "SELECT id, ts, topic, payload, seq, event_id, attempts FROM buffer WHERE synced=0 ORDER BY seq ASC LIMIT ?",
                (limit,)
            )
            return cur.fetchall()

    def mark_synced(self, row_id: int):
        with self._lock:
            self._conn.execute(
                "UPDATE buffer SET synced=1, synced_at=? WHERE id=?",
                (datetime.now(timezone.utc).isoformat(), row_id)
            )
            self._conn.commit()

    def record_failure(self, row_id: int, error: str):
        with self._lock:
            self._conn.execute("UPDATE buffer SET attempts=attempts+1, last_error=? WHERE id=?", (error[:500], row_id))
            self._conn.commit()

    def failure_log(self):
        with self._lock:
            cur = self._conn.execute("SELECT event_id, seq, attempts, last_error FROM buffer WHERE attempts > 0 ORDER BY seq")
            return [dict(row) for row in cur.fetchall()]

    def stats(self):
        with self._lock:
            pending = self._conn.execute("SELECT COUNT(*) FROM buffer WHERE synced=0").fetchone()[0]
            total = self._conn.execute("SELECT COUNT(*) FROM buffer").fetchone()[0]
            return {"pending": pending, "total": total}

    def close(self):
        with self._lock:
            self._conn.close()

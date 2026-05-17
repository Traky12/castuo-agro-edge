import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

class BufferDB:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
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
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_buffer_synced_id ON buffer(synced, id)")
            self._conn.commit()

    def enqueue(self, topic: str, payload: dict):
        with self._lock:
            self._conn.execute(
                "INSERT INTO buffer (ts, topic, payload, synced) VALUES (?, ?, ?, 0)",
                (datetime.now(timezone.utc).isoformat(), topic, json.dumps(payload, ensure_ascii=False))
            )
            self._conn.commit()

    def pending(self, limit: int = 100):
        with self._lock:
            cur = self._conn.execute(
                "SELECT id, ts, topic, payload FROM buffer WHERE synced=0 ORDER BY id ASC LIMIT ?",
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

    def stats(self):
        with self._lock:
            pending = self._conn.execute("SELECT COUNT(*) FROM buffer WHERE synced=0").fetchone()[0]
            total = self._conn.execute("SELECT COUNT(*) FROM buffer").fetchone()[0]
            return {"pending": pending, "total": total}

    def close(self):
        with self._lock:
            self._conn.close()

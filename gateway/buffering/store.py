"""Offline buffer — SQLite first; Timescale optional for Pi deployments."""

import sqlite3
from pathlib import Path

from gateway.config import settings


def init_buffer() -> None:
    path = Path(settings.buffer_sqlite_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                synced INTEGER DEFAULT 0
            )
            """
        )
        conn.commit()

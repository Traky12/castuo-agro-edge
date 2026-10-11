import logging
import time
from datetime import datetime, timezone

import requests

logger = logging.getLogger("castuo.edge.sync")


class SyncWorker:
    def __init__(self, db, backend_url: str, api_key: str, device_id: str, batch_size: int = 100):
        self.db = db
        self.backend_url = backend_url.rstrip("/")
        self.api_key = api_key
        self.device_id = device_id
        self.batch_size = batch_size
        self._stop = False
        self._backoff = 30

    def stop(self):
        self._stop = True

    def run_once(self):
        if not self.backend_url or not self.api_key:
            return False
        rows = self.db.pending(self.batch_size)
        if not rows:
            self._backoff = 30
            return True
        ok_any = False
        for row in rows:
            payload = {
                "event_id": row["event_id"],
                "seq": row["seq"],
                "device_id": self.device_id,
                "gateway_ts": datetime.now(timezone.utc).isoformat(),
                "source_ts": row["ts"],
                "topic": row["topic"],
                "payload": row["payload"],
            }
            error = None
            try:
                r = requests.post(
                    f"{self.backend_url}/api/v1/sensores/ingest",
                    json=payload,
                    headers={
                        "X-API-Key": self.api_key,
                        "X-Device-ID": self.device_id,
                        # The core must treat a repeated key as the same event, not a new one.
                        "Idempotency-Key": row["event_id"],
                    },
                    timeout=15,
                )
                if r.status_code in (200, 201, 202):
                    self.db.mark_synced(row["id"])
                    ok_any = True
                    continue
                error = f"HTTP {r.status_code}"
            except requests.RequestException as exc:
                error = f"{type(exc).__name__}: {exc}"
            self.db.record_failure(row["id"], error)
            logger.warning("sync failed for event %s (seq %s): %s", row["event_id"], row["seq"], error)
            break  # keep order: retry from this event on the next round
        self._backoff = 30 if ok_any else min(self._backoff * 2, 300)
        return ok_any

    def run_forever(self):
        while not self._stop:
            self.run_once()
            time.sleep(self._backoff)

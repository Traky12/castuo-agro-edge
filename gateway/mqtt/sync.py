import json
import logging
import time
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

import requests

logger = logging.getLogger("castuo.edge.sync")

# Must remain aligned with apps/api/iot_pipeline/schemas.py SensorPayloadIn.
_SENSOR_FIELDS = frozenset(
    {
        "ph",
        "ec",
        "temp_agua",
        "co2",
        "luz_par",
        "o2_disuelto",
        "temperatura",
        "temperature",
        "humedad",
        "humidity",
        "humedad_suelo",
        "soil_moisture",
        "soil_1",
        "soil_2",
        "soil_3",
    }
)
_REQUIRED_SENSOR_FIELDS = _SENSOR_FIELDS
_ALLOWED_CONTEXT_FIELDS = frozenset(
    {"schema_version", "message_id", "device_timestamp", "tray_id", "bandeja"}
)


def _build_ingest_payload(row, device_id: str) -> dict:
    """Adapt an MQTT reading to the canonical IoT API contract.

    The message ID is stable for correlation across retries. The canonical API
    currently stores message_id as trace metadata; it does not promise durable
    deduplication, so this adapter provides ordered at-least-once delivery only.
    """
    try:
        raw = json.loads(row["payload"])
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("buffered MQTT payload is not valid JSON") from exc
    if not isinstance(raw, dict):
        raise ValueError("buffered MQTT payload must be a JSON object")

    values = dict(raw)
    # Accept known wrapper forms, preferring explicit top-level sensor fields.
    for wrapper in ("sensors", "readings", "payload"):
        nested = values.get(wrapper)
        if isinstance(nested, dict):
            values = {**nested, **values}

    sensors = {
        key: values[key]
        for key in _SENSOR_FIELDS
        if key in values and values[key] is not None
    }
    if not any(key in sensors for key in _REQUIRED_SENSOR_FIELDS):
        raise ValueError("buffered payload has no recognized sensor readings")

    message_id = str(uuid5(NAMESPACE_URL, f"castuo-edge-event:{row['event_id']}"))
    payload = {
        "schema_version": values.get("schema_version") or "iot.v1",
        "message_id": message_id,
        **sensors,
    }

    device_timestamp = values.get("device_timestamp")
    if device_timestamp is None:
        candidate = values.get("timestamp", values.get("ts"))
        if isinstance(candidate, str):
            device_timestamp = candidate
    if device_timestamp is not None:
        payload["device_timestamp"] = device_timestamp

    tray_id = values.get("tray_id", values.get("bandeja"))
    if tray_id is not None:
        payload["tray_id"] = tray_id

    original_metadata = values.get("metadata")
    metadata = dict(original_metadata) if isinstance(original_metadata, dict) else {}
    metadata.update(
        {
            "edge_event_id": row["event_id"],
            "edge_seq": row["seq"],
            "edge_topic": row["topic"],
            "edge_enqueued_at": row["ts"],
            "edge_device_id": device_id,
            "delivery_semantics": "at-least-once",
        }
    )
    payload["metadata"] = metadata
    return payload


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
            try:
                payload = _build_ingest_payload(row, self.device_id)
                response = requests.post(
                    f"{self.backend_url}/api/v1/iot/data",
                    json=payload,
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    timeout=15,
                )
                if response.status_code in (200, 201, 202):
                    self.db.mark_synced(row["id"])
                    ok_any = True
                    continue
                error = f"HTTP {response.status_code}"
            except (requests.RequestException, ValueError, TypeError) as exc:
                error = f"{type(exc).__name__}: {exc}"

            self.db.record_failure(row["id"], error)
            logger.warning(
                "sync failed for event %s (seq %s): %s",
                row["event_id"],
                row["seq"],
                error,
            )
            break  # Preserve ordering: retry this event before later events.

        self._backoff = 30 if ok_any else min(self._backoff * 2, 300)
        return ok_any

    def run_forever(self):
        while not self._stop:
            self.run_once()
            time.sleep(self._backoff)

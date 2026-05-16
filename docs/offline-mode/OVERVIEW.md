# Offline mode

## Behaviour

When upstream (`CASTUO_API_URL`) is unreachable:

1. MQTT ingestion continues into the local broker.
2. Gateway writes readings to `telemetry_queue` (SQLite).
3. Actuator commands from **local rules** or **edge_ai/local_rules** still execute.
4. Health endpoint reports `offline_capable: true` and queue depth (v0.1+).

When connectivity returns:

1. `gateway.sync.upstream` drains the queue in batches (`SYNC_BATCH_SIZE`).
2. Conflicts resolve **core wins** for configuration; **edge wins** for timestamps already committed locally.
3. No data is deleted from edge buffer until core ACK.

## Operator checklist

- Confirm `BUFFER_SQLITE_PATH` on persistent volume (Pi: `/data`).
- Set `SITE_ID` unique per deployment.
- Test: `docker compose up` → disconnect WAN → publish MQTT → reconnect → verify sync.

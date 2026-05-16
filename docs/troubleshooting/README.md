# Troubleshooting

| Symptom | Check |
|---------|--------|
| Gateway unhealthy | `curl localhost:8080/health` |
| No MQTT messages | `mosquitto_sub -h localhost -t 'castuo/edge/#' -v` |
| Buffer not growing | `BUFFER_SQLITE_PATH` writable, `gateway.buffering.store.init_buffer()` |
| Sync idle | `CASTUO_API_URL` and `CASTUO_API_KEY` set |
| ESP32 silent | Serial monitor, Wi‑Fi creds in `hardware/esp32/` template |

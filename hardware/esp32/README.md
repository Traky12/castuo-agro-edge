# ESP32 telemetry templates

Publish JSON to `castuo/edge/{device_id}/telemetry`:

```json
{"device_id":"esp32-01","readings":{"ph":6.2,"ec":1.8,"temperatura":24.5}}
```

Templates and `.ino` sketches land in v0.1 roadmap. Align pin maps with `hardware/wiring/`.

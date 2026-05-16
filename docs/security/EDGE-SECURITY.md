# Edge security

- No secrets in git; use `.env` only on device.
- MQTT: enable auth in production (`deployment/docker/mosquitto.conf` — disable `allow_anonymous`).
- TLS termination at reverse proxy or Mosquitto 8883 for field Wi‑Fi exposure.
- `CASTUO_API_KEY` rotated per site; least privilege on core API.
- Firmware OTA (v0.3): signed images only.

Align with CASTÚO-SYSTEM kernel: EU data residency, no US LLM endpoints on edge inference paths.

# Raspberry Pi gateway profile

Recommended: Pi 4/5, 64-bit Raspberry Pi OS, Docker Compose stack from repo root.

- Mount `/data` for SQLite buffer persistence.
- Optional: USB SSD for Timescale edge buffer.
- systemd unit: `deployment/systemd/castuo-edge.service` (v0.1).

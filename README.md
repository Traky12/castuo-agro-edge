# CASTUO Agro Edge

**Offline-first rural edge computing stack for agritech and environmental monitoring.**

CASTUO Agro Edge is the operational edge layer of [CASTÚO-SYSTEM](https://github.com/Traky12/Castuo-system): it runs where connectivity is unreliable, sovereignty matters, and telemetry must survive disconnections.

## Overview

CASTUO Agro Edge provides a resilient operational layer for distributed agricultural and environmental systems operating in unstable or low-connectivity environments.

The platform is designed for:

- hydroponics
- greenhouse automation
- agrovoltaics
- forestry monitoring
- dehesa ecosystems
- environmental telemetry
- rural infrastructure automation

## Core features

- MQTT telemetry ingestion
- Offline buffering and synchronization
- Raspberry Pi gateway support
- ESP32 / ESP32-S3 integration
- Local relay and actuator control
- Edge AI inference (optional)
- Sensor orchestration
- Secure telemetry pipelines
- Resilient offline-first architecture

## Technology stack

| Layer | Technology |
|-------|------------|
| Gateway | Python 3.11+, FastAPI |
| Messaging | MQTT (Mosquitto) |
| Buffer | SQLite / TimescaleDB (edge) |
| Containers | Docker, Compose |
| Hardware | Raspberry Pi, ESP32 |
| AI (optional) | Mistral AI EU |
| Core sync | CASTÚO-SYSTEM API / GaiaChain (planned) |

## Repository layout

```text
castuo-agro-edge/
├── gateway/          # MQTT, buffering, sync, telemetry, health, storage
├── edge_ai/          # Local inference, rules, irrigation logic
├── hardware/         # Pi, ESP32, sensors, relays, wiring guides
├── protocols/        # MQTT, Modbus, LoRa, HTTP adapters
├── deployment/       # Docker, k3s, Hetzner, systemd
├── docs/             # Architecture, offline mode, security
└── examples/         # Hydroponics, greenhouse, dehesa, livestock
```

## Quick start

```bash
cp .env.example .env
docker compose up -d
curl http://localhost:8080/health
```

See `docs/architecture/EDGE-STACK.md` and `docs/offline-mode/OVERVIEW.md`.

## Relationship to CASTÚO-SYSTEM

| This repo (edge) | Castuo-system (core) |
|------------------|----------------------|
| Ingest, buffer, actuate locally | API, n8n, PostgreSQL, SABIONDA OMEGA |
| Offline-first | Cloud / Hetzner EU orchestration |
| ESP32 / Pi profiles | TRL9 integration, compliance, dashboards |

Edge devices sync upstream when connectivity returns; they never require permanent cloud access for critical loops.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for v0.1 milestones.

## License

License pending definition. See [LICENSE](LICENSE).

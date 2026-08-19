# 📡 castuo-agro-edge — Resilient Rural IoT Stack

![Status](https://img.shields.io/badge/Status-Active%20Engineering-blue)
![Maturity](https://img.shields.io/badge/Maturity-v0.1%20(Impl)-informational)
![License](https://img.shields.io/badge/License-Pending-lightgrey)

> **Offline-first rural edge computing stack for agritech and environmental monitoring.**

---

## 1. Purpose & Scope
**castuo-agro-edge** is the operational edge layer of the ecosystem. It is designed to run in environments where connectivity is unreliable, sovereignty matters, and telemetry must survive disconnections.

Its scope covers:
- **MQTT Telemetry Ingestion:** Local sensor data handling.
- **Offline Buffering:** Data persistence during disconnection periods.
- **Hardware Integration:** Support for Raspberry Pi gateways and ESP32 nodes.
- **Edge Orchestration:** Sensor management and local actuation loops.

---

## 2. Ecosystem Position
castuo-agro-edge acts as the **EDGE** layer, providing field evidence and telemetry to the core platform.

```text
castuo-agro-edge (Edge)
     │
     ├── castuo-evidence (Public Fabric)
     │      Evidence verification surface
     │
     ├── CASTÚO-SYSTEM (Private Core)
     │      Upstream sync target
     │
     └── castuo-evolution (Control Plane)
            Governance & SSOT
```

---

## 3. Technology Stack
| Layer | Technology |
| :--- | :--- |
| **Gateway** | Python 3.11+, FastAPI |
| **Messaging** | MQTT (Mosquitto) |
| **Buffer** | SQLite / TimescaleDB (edge) |
| **Hardware** | Raspberry Pi, ESP32, LoRaWAN |
| **Containers** | Docker, Compose |
| **AI (optional)** | Mistral AI EU |

---

## 4. Engineering & Evidence
Following the **Evidence-First** principle, this repository focuses on providing reproducible field data.
- **Implemented:** MQTT ingestion, local buffering, and Pi gateway support.
- **Planned:** Full end-to-end synchronization with GaiaChain/Core.

Maturity is tracked through the **G0-G7 Gates** in the governance plane (`castuo-evolution`).

---

## 5. Quick Start
```bash
cp .env.example .env
docker compose up -d
curl http://localhost:8080/health
```

---

## 6. Navigation
[← Profile](https://github.com/Traky12) | [→ Evidence](https://github.com/Traky12/castuo-evidence) | [→ Governance](https://github.com/Traky12/castuo-evolution) | [→ Architecture Docs](docs/architecture/EDGE-STACK.md)

---

## 🌐 Connect
- 🌍 [Website](https://castuo-system.es/)
- 📡 [Edge Stack](https://github.com/Traky12/castuo-agro-edge)

**Build · Validate · Observe · Document · Evolve**

## Architecture governance boundary

This repository is governed through the CASTÚO-SYSTEM evidence chain. Its current role, visibility boundary, required provenance, security baseline and promotion rules are defined in [`docs/CASTUO_ARCHITECTURE_GOVERNANCE.md`](docs/CASTUO_ARCHITECTURE_GOVERNANCE.md). A repository artifact or green workflow proves only the declared scope; it does not by itself prove certification, production operation, funding, customer contracts or commercial success.

## Federated edge operation

The edge node is an independent trust boundary. Its readiness model is explicit:

| State | Meaning |
|---|---|
| `LOCAL_OPERATION_IMPLEMENTED` | Local ingestion or buffering exists within the declared repository scope |
| `PILOT_PREPARED` | A bounded field protocol and evidence package are prepared |
| `FEDERATION_PENDING` | No second real node, tested exchange or synchronisation evidence has yet been verified |

Offline operation uses device identity, encrypted local buffering, an idempotent queue, replay protection, revocation and preserved conflicts. Connectivity loss must not turn an unapproved critical action into an approved one. Physical actuation remains blocked without current policy authorisation and, when required, human approval.

## Private-cloud and evidence boundary

This repository is part of the CASTÚO-SYSTEM private-cloud target architecture. Its repository scope does not by itself prove cloud provisioning, DNS, production operation, customer traction, financing, certification or independent validation. The service identity is a governed target boundary until a deployment record, access control, health check, observability, backup, restore, rollback, owner and dated Evidence Center record are published.

The public state model is `DOCUMENTED` → `IMPLEMENTED_LOCAL` → `TESTED` → `VALIDATED` → `OPERATIONAL`. OpenClaw and n8n, where referenced, are optional compatibility adapters and not the sovereign governance control plane.\n

<!-- CASTUO:PUBLIC-SURFACE -->
## CASTÚO integration boundary

This repository exposes only a bounded public integration surface. Its role, current state and claims are subordinate to the `Traky12/castuo-evolution` control plane.

This repository does not by itself claim production operation, certification, independent validation, customer contracts, revenue, autonomous authority, global federation or legal compliance. Do not publish secrets, credentials, private endpoints, customer data, private evidence or unpublished security findings.

See [`docs/CASTUO_PUBLIC_SURFACE.md`](docs/CASTUO_PUBLIC_SURFACE.md) for the public boundary. `Claim != Evidence`; `CURRENT != TARGET`; promotion requires control-plane authorization.
<!-- CASTUO:PUBLIC-SURFACE-END -->

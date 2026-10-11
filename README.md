<!-- CASTUO:BRAND:START -->
<p align="center">
  <img src="https://raw.githubusercontent.com/Traky12/Traky12/main/assets/brand/castuo-system-logo-square.jpg" alt="CASTÚO-SYSTEM official logo" width="180" />
</p>
<!-- CASTUO:BRAND:END -->

# 📡 castuo-agro-edge — Resilient Rural IoT Stack

![Status](https://img.shields.io/badge/Status-Active%20Engineering-blue)
![Maturity](https://img.shields.io/badge/Maturity-v0.1%20(Impl)-informational)
![License](https://img.shields.io/badge/License-Pending-lightgrey)

> **Offline-first rural edge computing stack for agritech and environmental monitoring.**

---

## Architectural identity

- **Architectural name:** `castuo-edge-telemetry`
- **Role:** Edge/IoT telemetry, local buffering and device integration.
- **Boundary:** Declared edge and telemetry scope; product-market regulatory applicability remains assessment-dependent.
- **Status:** `CURRENT` within declared scope.
- **Quality profile:** [`.castuo/repository-profile.yaml`](.castuo/repository-profile.yaml)

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
     └── castuo-evolution (experimental)
            Governance framework — not the current SSOT
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

Maturity is tracked through the **G0-G7 Gates** defined in the canonical governance of CASTÚO-SYSTEM (`Castuo-system/governance/`, private). `castuo-evolution` is an experimental governance and evolution framework; it is not the current source of truth or a deployed control plane.

---

## 5. Quick Start
```bash
cp .env.example .env
docker compose up -d
curl http://localhost:8080/health
```

---

## 6. Navigation
[← Profile](https://github.com/Traky12) | [→ Evidence](https://github.com/Traky12/castuo-evidence) | [→ Governance framework (experimental)](https://github.com/Traky12/castuo-evolution) | [→ Architecture Docs](docs/architecture/EDGE-STACK.md)

---

## 🌐 Connect
- 🌍 [Website](https://castuo-system.es/)
- 📡 [Edge Stack](https://github.com/Traky12/castuo-agro-edge)

**Build · Validate · Observe · Document · Evolve**

## Architecture governance boundary

This repository is governed through the CASTÚO-SYSTEM evidence chain. Its current role, visibility boundary, required provenance, security baseline and promotion rules are defined in [`docs/CASTUO_ARCHITECTURE_GOVERNANCE.md`](docs/CASTUO_ARCHITECTURE_GOVERNANCE.md). A repository artifact or green workflow proves only the declared scope; it does not by itself prove certification, production operation, funding, customer contracts or commercial success.

## Edge operation and federation readiness (TARGET)

> **Federation is a TARGET, not a current capability.** No second real node, tested exchange or synchronisation evidence has been verified (`FEDERATION_PENDING`).

The edge node is an independent trust boundary. Its readiness model is explicit:

| State | Meaning |
|---|---|
| `LOCAL_OPERATION_IMPLEMENTED` | Local ingestion or buffering exists within the declared repository scope |
| `PILOT_PREPARED` | A bounded field protocol and evidence package are prepared |
| `FEDERATION_PENDING` | No second real node, tested exchange or synchronisation evidence has yet been verified |

Target design for offline operation (not a statement of what is implemented; see the evidence links for verified scope): device identity, encrypted local buffering, an idempotent queue, replay protection, revocation and preserved conflicts. Connectivity loss must not turn an unapproved critical action into an approved one. Physical actuation remains blocked without current policy authorisation and, when required, human approval.

## Private-cloud and evidence boundary

This repository is part of the CASTÚO-SYSTEM private-cloud target architecture. Its repository scope does not by itself prove cloud provisioning, DNS, production operation, customer traction, financing, certification or independent validation. The service identity is a governed target boundary until a deployment record, access control, health check, observability, backup, restore, rollback, owner and dated Evidence Center record are published.

The public state model is `DOCUMENTED` → `IMPLEMENTED_LOCAL` → `TESTED` → `VALIDATED` → `OPERATIONAL`. OpenClaw and n8n, where referenced, are optional compatibility adapters and not the sovereign governance control plane.\n

<!-- CASTUO-GOVERNED-README-BLOCK:START -->
## CASTÚO-SYSTEM evidence and claim boundary

This repository is the edge/IoT adapter surface for local telemetry and rural connectivity constraints. A repository description, test result or green workflow proves only the exact scope tested; it does not prove field operation, independent assurance or production readiness.

### Authority and repository roles

- **Canonical technical state, governance and promotion decisions:** [Traky12/Castuo-system](https://github.com/Traky12/Castuo-system) (private authority).
- **Public offline evidence verification:** [castuo-e3-001 / e3bundle](https://github.com/Traky12/castuo-e3-001). It verifies declared file integrity and signatures; it is not a certification authority or a source of field evidence by itself.
- **Assurance and CI tooling:** [goldfish](https://github.com/Traky12/goldfish) and [Cast-o](https://github.com/Traky12/Cast-o); local or automated results remain bounded to their recorded checks.
- **castuo-evolution:** experimental/historical governance material; it is not the current technical authority for this repository.

### Current evidence boundary

| Dimension | Current declared state |
|---|---|
| Repository role | Edge / IoT integration |
| Implementation maturity | Candidate; only explicitly tested behavior may be called implemented |
| Evidence and security | Evidence pending outside the checks recorded on each commit |
| Field pilot and multi-node federation | Pending independent, replayable field evidence |
| Production, certification and commercial validation | Not claimed |
| Promotion | Blocked until scope-specific evidence, review and rollback criteria are satisfied |

### Promotion sequence

`CAPABILITY → CONTRACT → IMPLEMENTATION → TEST → EVIDENCE → REPLAY → REVIEW → PROMOTION`

A promotion requires evidence for the same commit, environment and scope, plus review and a recovery/rollback path. Historical snapshots, roadmap items, badges and copied repository descriptions are not operational evidence.

### References

- [Edge stack architecture](docs/architecture/EDGE-STACK.md)
- [Repository governance boundary](docs/CASTUO_ARCHITECTURE_GOVERNANCE.md)
- [Staging and operational boundaries](docs/STAGING.md)

<!-- CASTUO-GOVERNED-README-BLOCK:END -->

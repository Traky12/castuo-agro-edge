<!-- CASTUO:BRAND:START -->
<p align="center">
  <img src="https://raw.githubusercontent.com/Traky12/Traky12/main/assets/brand/castuo-system-logo-square.jpg" alt="CASTÚO-SYSTEM official logo" width="180" />
</p>
<!-- CASTUO:BRAND:END -->

# 📡 castuo-agro-edge — Resilient Rural IoT Stack

![Status](https://img.shields.io/badge/Status-Active%20Engineering-blue)
![Claims](https://img.shields.io/badge/Claims-see%20status%20table-informational)
![License](https://img.shields.io/badge/License-Pending%20IP%20review-lightgrey)

> **Offline-first rural edge computing stack for agritech and environmental monitoring.**

> **License: pending IP review.** This repository is **not** open source. Its `LICENSE` file states "License Pending … All rights reserved until a license is selected"; no license has been granted and the rights holder is still to be formally identified. External contributions are not accepted until a contributor licence agreement (CLA) or contribution policy is defined.

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
castuo-agro-edge is designed as the **EDGE** layer that will provide field telemetry to the core platform. No real field data has been produced yet.

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

**Canonical authority:** `Castuo-system` (private) is the current authority for code, operational documentation and technical evolution. `castuo-evolution` is a prepared external surface.

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
Statuses use the CASTÚO taxonomy: `CURRENT` (implemented and verifiable) · `TARGET` (approved, not implemented) · `EXPERIMENTAL` · `PENDING` (planned, or evidence incomplete) · `NOT_CLAIMED`.

| Claim | Status | Evidence / limitation |
|---|---|---|
| Gateway health endpoint (`/health`, offline-capable flag) | `CURRENT` | `tests/unit/test_health.py`: 1 passed (commit `73db95d`, local, 2026-09-28) |
| MQTT ingestion (`gateway/mqtt/`) | `PENDING` — implemented, unverified | Code present; no tests or execution evidence |
| Local offline buffering (`gateway/buffering/store.py`) | `PENDING` — implemented, unverified | Code present; no tests or execution evidence |
| Upstream sync (`gateway/sync/upstream.py`) | `PENDING` — implemented, unverified | Code present; no tests or execution evidence |
| Raspberry Pi gateway (Dockerfile, systemd unit) | `PENDING` — implemented, unverified | No hardware run evidence |
| ESP32 firmware (`firmware/`) | `EXPERIMENTAL` | Sketch present; no hardware run evidence |
| Field telemetry from a real deployment | `NOT_CLAIMED` | No real field data yet |
| Integration with `castuo-evolution` | `NOT_CLAIMED` | No verifiable mechanism |
| Security baseline | `PENDING` — documented, not validated | [`SECURITY.md`](SECURITY.md) and `docs/CASTUO_ARCHITECTURE_GOVERNANCE.md`; no security testing evidence |
| End-to-end sync with GaiaChain / Core | `TARGET` | Not implemented |

Code being present does not mean a capability is validated.

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

<!-- CASTUO:PUBLIC-SURFACE -->
## CASTÚO integration boundary

This repository exposes only a bounded public integration surface. Its role, current state and claims are subordinate to the `Traky12/castuo-evolution` control plane.

This repository does not by itself claim production operation, certification, independent validation, customer contracts, revenue, autonomous authority, global federation or legal compliance. Do not publish secrets, credentials, private endpoints, customer data, private evidence or unpublished security findings.

See [`docs/CASTUO_PUBLIC_SURFACE.md`](docs/CASTUO_PUBLIC_SURFACE.md) for the public boundary. `Claim != Evidence`; `CURRENT != TARGET`; promotion requires control-plane authorization.
<!-- CASTUO:PUBLIC-SURFACE-END -->

<!-- CASTUO-PUBLIC-INTEGRATION:START -->
## CASTÚO-SYSTEM public integration

**Repository role:** Edge layer.

Capacidades edge acotadas y verificables. The public reference surface is governed by the [Traky12 profile](https://github.com/Traky12/Traky12) and the [castuo-evolution control plane](https://github.com/Traky12/castuo-evolution). Current ecosystem status is documented in the [integration status](https://github.com/Traky12/castuo-evolution/blob/main/docs/GITHUB_INTEGRATION_STATUS_2026-08-16.md) and [blocker register](https://github.com/Traky12/castuo-evolution/blob/main/docs/GITHUB_INTEGRATION_BLOCKERS_2026-08-16.md).

> Identity is not evidence. Repository activity is not operational truth. No production, certification, legal-compliance, customer, revenue, continuous-operation or federation claim is implied by this README block.
<!-- CASTUO-PUBLIC-INTEGRATION:END -->

<!-- CASTUO:ECOSYSTEM-INTEGRATION:START -->
## CASTÚO-SYSTEM ecosystem integration

**Declared role:** Edge e IoT para continuidad de campo.

This repository is connected to the CASTÚO-SYSTEM ecosystem through the [Traky12 public profile](https://github.com/Traky12), the [Castuo-system core](https://github.com/Traky12/Castuo-system), and the [castuo-evolution governance control plane](https://github.com/Traky12/castuo-evolution). The canonical map defines relationships; repository activity does not become operational evidence by itself.

**Current bounded state:** GREEN-STAGING-CANDIDATE · EVIDENCE-SCOPED · PROMOTION-BLOCKED, unless this repository's own metadata declares a narrower state. Identity, implementation, tests, evidence, review and promotion remain separate dimensions.

**Evidence boundary:** This README does not claim production operation, certification, legal compliance, independent validation, customer traction, revenue, continuous operation, autonomous authority or federation. Such claims require scope-bound provenance, reproducible artifacts, security review, human review and an explicit promotion decision.

**Canonical references:** [CASTÚO-REPOSITORY-STANDARD-V1.0](https://github.com/Traky12/Castuo-system/blob/main/README.md), [CASTÚO public claim boundary](https://github.com/Traky12/Traky12/blob/main/PUBLIC_CLAIM_BOUNDARY.md), and the [public profile](https://github.com/Traky12/Traky12).
<!-- CASTUO:ECOSYSTEM-INTEGRATION:END -->

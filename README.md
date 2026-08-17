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
     ├── CASTÚO-SYSTEM (Core)
     │      Upstream sync target
     │
     ├── ctaex-iot-pilot (Pilot)
     │      Validation environment
     │
     └── GOLDfish (Assurance)
            Security & validation gate
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
[← Ecosystem Profile](https://github.com/Traky12) | [→ Core Platform](https://github.com/Traky12/Castuo-system) | [→ Governance](https://github.com/Traky12/castuo-evolution) | [→ Architecture Docs](docs/architecture/EDGE-STACK.md)

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

<!-- CASTUO-GOVERNED-README-BLOCK:START -->
## CASTÚO-SYSTEM governed operating model

This repository is part of the CASTÚO-SYSTEM evidence operating system. Its status is governed by implementation, evidence and promotion gates; repository presence or vendor language is not evidence of operational maturity.

### Three-plane architecture

| Plane | Role | Repository boundary |
|---|---|---|
| Internal control plane | Capabilities, evidence, claims, gates, passports and N3/N4/N5/N6 maturity | This repository's contracts and governed records |
| Competitive intelligence | 1/0/?/N/A comparison, 1D/1V/1R semantics, scenarios and sensitivity | Comparative records remain bounded by provenance |
| External validation | Independent review, reproducible benchmark, field pilot, KPIs and economic evidence | Promotion requires reviewable external evidence |

### Claim discipline

`CAPABILITY` is not `EVIDENCE`; `EVIDENCE` is not `MATURITY`; `MATURITY` is not `CLAIM`; and `CLAIM` is not `COMPETITIVE ADVANTAGE`. The binary matrix uses `1D` for primary-source declaration, `1V` for reproducible verification, `1R` for independent reproduction, `?` for unknown, `0` for absent in the tested boundary and `N/A` for non-comparable scope. Unknown is never silently converted into absence or proof.

### Reproducibility benchmark

The current competitive protocol is **S-001 Evidence-Ready Field Operations**: the same operational task, inputs and connectivity failure condition are replayed through CASTÚO and an alternative implementation. Its metrics cover continuity, recovery, provenance, evidence completeness, reviewability and claim generation. `P2` versions the fixture, `E3` requires independent replay and `N5` requires a signed field pilot with KPIs. A local fixture result is labelled `LOCAL REPRODUCTION / NO FIELD CLAIM`.

### Implemented progress surface

The governed integration currently covers the following evidence-scoped capabilities:

| Capability | Current state | Boundary |
|---|---|---|
| Secure SaaS connectors | Vault-first intents, rotation, revocation, owner isolation, least-privilege scopes and redacted audit | Real provider selection remains `SECURITY_HOLD` until dual approval |
| Quantum Decision Lab | Deterministic local simulator with evidence budget, heuristic confidence and factor readouts | `LOCAL RESULT / NO CLAIM`; no field or economic evidence implied |
| Assurance P0/P1/P2 | Roadmap, Trust Passports, AI Security Passport, SLO/observability contracts and open-gate register | External review, production restore and remote assurance remain pending |
| Competitive intelligence | 1/0/?/N/A matrix, weighted coverage, evidence completeness and 17 capability passports | `?` is uncertainty; it is never silently converted to 0 or 1 |
| S-001 reproducibility benchmark | Same task, inputs and failure condition; continuity, recovery, provenance, completeness, reviewability and claim generation | P2 fixture, E3 independent replay and N5 field/economic evidence are separate gates |
| Supply-chain controls | Secret scan, SBOM, dependency scan and local dependency result of 0 advisories | Local green status does not prove remote GitHub Security and quality is 0 |
| Traky12 integration | 16 remote repositories classified; 14 governed README PRs open and traceable | Protected main branches require review/checks; forks are excluded |

### Current boundary

Claims remain evidence-scoped. Do not describe this repository as production-validated, best-in-class, independently reviewed, commercially superior or N5/N6 unless the corresponding passport, evidence package, signed review and gate record are present. The open-gate register is authoritative for vault approval, GitHub security access, remote alerts, production restore, diagnostics and external validation.

### Traceability

| Artifact | Purpose |
|---|---|
| `TRAKY12-README-INVENTORY.json` | Repository surface, sensitivity and evidence classification |
| `Competitive Capability Passport` | Capability state, provenance, maturity and forbidden claims |
| `S-001 benchmark` | Reproducible comparison protocol and promotion boundary |
| P0/P1/P2 roadmap | Exit criteria and rollback responsibility |
| `Dashboard checkpoint` | Restorable implementation state and validation result |
| `CASTUO-SYSTEM-OPERATING-INDEX.md` | Master operating plan, task registry, gates, claims boundary, checkpoints and repository traceability |

The master operating index is available at [`docs/governance/CASTUO-SYSTEM-OPERATING-INDEX.md`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-SYSTEM-OPERATING-INDEX.md). This block is a governed integration reference. Repository-specific build, deployment, security and operational instructions remain authoritative in the rest of this README.
<!-- CASTUO-GOVERNED-README-BLOCK:END -->

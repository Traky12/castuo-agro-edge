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

### Sovereign reference architecture

CASTÚO-SYSTEM uses an explicit authority hierarchy: `todo.md` records the operational backlog; `CASTUO-SYSTEM-OPERATING-INDEX.md` governs architecture, gates and claims; typed contracts and passports define executable semantics; tests, scans, SBOM and benchmarks provide bounded evidence; PR reviews and protected branches govern change; independent, field and economic evidence are required for E3/N5 promotion. A higher-level source is authoritative only within its domain: a README cannot override a contract, a local test cannot convert a remote 403 into zero alerts, and a commit reference is not field evidence.

Ownership is explicit. Platform owns dashboard and contracts; governance owns README and index; assurance owns passports and claims; security owns vault and connectors; repository maintainers own remote Security and quality; independent reviewers and pilot owners own E3/N5 evidence. Every change follows `task → artifact → branch → commit → PR → review/checks → merge → checkpoint → passport`. No automation may self-approve, merge protected branches, register secrets or promote claims without the required gate.

The sovereignty reference is [`docs/governance/CASTUO-SOVEREIGN-REFERENCE-ARCHITECTURE.md`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-SOVEREIGN-REFERENCE-ARCHITECTURE.md). It defines data sovereignty, external dependency boundaries, recovery rules and rollback responsibilities. The machine-readable change policy is [`docs/governance/CASTUO-COMMIT-GOVERNANCE-POLICY.json`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-COMMIT-GOVERNANCE-POLICY.json); it is normative for commit messages, PR review, required checks, ownership, claim boundaries and rollback.

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

### Integral improvement and sovereign state

CASTÚO-SYSTEM evolved from dispersed repositories and capabilities into a control plane governed by evidence, security and controlled promotion. Its shared sequence is `ecosystem → public index → capability → contract → implementation → evidence → security → trust passport → promotion gate → negative evidence`. The system distinguishes implementation, documentation, validation, maturity, promotion and authorized claims.

The current sovereign model defines one system with explicit roles: `Castuo-system` core, `castuo-evolution` governance, `Cast-o`/`goldfish` assurance and recovery, `castuo-offline-field-operations` field, `castuo-agro-edge` edge, and `Traky12` public baseline. Forks and upstream integrations are not proprietary capability. Security boundaries remain architectural: SaaS secrets stay backend-only behind an approved vault; local scans do not prove remote zero alerts.

The canonical improvement report is [`docs/governance/CASTUO-INTEGRAL-IMPROVEMENT-AND-SOVEREIGN-STATE.md`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-INTEGRAL-IMPROVEMENT-AND-SOVEREIGN-STATE.md). It records the evidence chain, binary competitive matrix, passports, maturity ceilings, recovery lineage and unresolved external gates. Current statuses remain `PENDING`, `SECURITY_HOLD`, `NOT_VERIFIED`, `EVIDENCE_REQUIRED` or `PROMOTION-BLOCKED` where external authorization or evidence is missing.

### OSS reputation and credibility

Reputation is treated as an output of real open-source work, not as a badge-collection target. The profile prioritises useful contributions, technical discussions, clear issues, cross-reviews, co-authored PRs, strong documentation, reproducible releases and organic external use. It does not create trivial PRs, artificial Discussions, mirror accounts, inflated activity, purchased badges or synthetic stars.

The public profile communicates **Founder & Lead Architect of CASTÚO-SYSTEM · Systems Architect · Evidence Engineer · AI Governance & Assurance** and presents CASTÚO as an evidence-governed control plane for distributed operations and AI-enabled systems. `Castuo-system` is the implementation lighthouse; `Traky12` is the public baseline/read-model. The 16-repository inventory is one modular system model, not 16 products. Achievements, stars, commits, releases or follower counts are activity signals, never proof of quality, production, adoption, security, independence or economic outcome.

The complete guardrail strategy is [`docs/governance/CASTUO-OSS-REPUTATION-STRATEGY.md`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-OSS-REPUTATION-STRATEGY.md). Its internal metrics are dated and bounded: useful contributions, valuable technical conversations, substantive co-authored PRs, documentation completeness, reproducible releases and organic interest in the lighthouse repository.

### Canonical public narrative

**CASTÚO-SYSTEM is an evidence-governed control plane for distributed operations and AI-enabled systems, with Evidence-Ready Field Operations as its first commercial wedge.** The first user journey is `Operate offline → preserve evidence → review → export`. This is a bounded product narrative, not a claim of production, customer adoption, field validation or commercial traction.

The public profile is a baseline and read-model: `public baseline → index → claims → evidence links → boundaries`. The 16-repository inventory is one modular system model, not 16 products. Repository roles and authority remain governed by the sovereign reference architecture and operating index.

The confidence progression is `evidence-scoped → independently reproduced → field validated → commercially validated`. The profile makes no comparative claim against named competitors and does not use best-in-class, commercial superiority, certification, autonomy or revenue language without a dated, scope-bound evidence passport. The canonical narrative is [`docs/governance/CASTUO-PUBLIC-NARRATIVE-AND-WEDGE.md`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-PUBLIC-NARRATIVE-AND-WEDGE.md).

### Maturity Acceleration Program G0→N6

The canonical maturity program prioritises evidence industrialisation over horizontal expansion. The order is `security → remote CI → vertical slice → observability/restore → E3 → pilot → payment → repeatability → N6`; a feature is prioritised only when it closes a P0, P1, P2, E3 or G-COMM gate. The program defines one canonical authority per category: `CASTUO-EVOLUTION` for governance, `Castuo-system` for core, `goldfish`/`Cast-o` for assurance, `castuo-offline-field-operations` for field, `castuo-agro-edge` for edge and `Traky12` for public read-model. Copies, workspaces, experiments and upstream forks are projections or non-canonical surfaces.

| Gate | Current boundary | Exit evidence |
|---|---|---|
| `R1-CI-REMOTE` | `BLOCKED` | Remote runner, logs, annotations, artifact, SHA, workflow ID, timestamp and reproducible failure |
| `P0-SECURITY` | `SECURITY_HOLD` | Backend-only vault, approved provider, rotation, revocation, least privilege, dual approval and audit completeness |
| `S-001` | `LOCAL RESULT / NO CLAIM` | Offline, duplicate, reorder, conflict, recovery, envelope, review and claim decision |
| `P1-OPS` | `EVIDENCE_REQUIRED` | Runtime SLOs, incidents, backup/restore checksum and replay |
| `P1-VENDOR-INDEPENDENCE` | `EVIDENCE_REQUIRED` | Same contract and inputs through Adapter A and Adapter B |
| `E3/GATE-R1` | `PENDING` | Frozen commit, fixture, instructions, negative tests, envelope and independent reproduction |
| `N5` | `PENDING` | PILOT-001, baseline, KPI, incident register, signed packets and independent review |
| `N6/G-COMM` | `BLOCKED` | Paid pilot, renewal, second customer/domain, replacement, multi-tenant hardening and SLA |

Evidence strength is `E0 claimed`, `E1 documented`, `E2 locally verified`, `E3 reproducibly verified`, `E4 independently reproduced`, `E5 field validated` and `E6 commercially validated`. The maturity ceiling follows `N3 ≤ E2`, `N4 ≤ E3`, `N5 requires E5` and `N6 requires E6`. `ECR = backed claims / attempted claims` should approach 1 and `Promotion Debt` should reach 0; until then, claims remain bounded.

The complete program is [`docs/governance/CASTUO-MATURITY-ACCELERATION-PROGRAM.md`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-MATURITY-ACCELERATION-PROGRAM.md). It freezes scope creep unless a change closes a named gate.

### Full operating plan transcription

The evolution plan is executed as a controlled chain rather than as an unbounded feature list. **Foundation** establishes repository boundaries, typed contracts, the dashboard and the capability vocabulary. **P0 Secure platform** enforces backend-only credential handling, vault-first intents, least-privilege permissions, rotation, revocation, owner isolation, redacted audit and supply-chain scanning. **P1 Evidence system** formalises sensitivity, provenance, Trust Passports, AI Security Passport, observability, SLOs, backup/restore and diagnostics. **P2 External validation** defines the second implementation, S-001 replay, independent review, field KPIs and economic evidence.

The operational backlog is maintained in `todo.md` and in the master operating index. Each task must preserve an owner, input boundary, expected output, exit criterion, evidence reference and rollback path. Completed work is marked without deleting historical entries. Blocked work remains visible with `BLOCKED`, `SECURITY_HOLD`, `EVIDENCE_REQUIRED` or `NOT_VERIFIED`; an open task is never evidence of capability.

| Control | Required transcription | Promotion rule |
|---|---|---|
| Capability | What the system can do and which repository owns it | Do not infer evidence from capability presence |
| Evidence | Source, contract, test, runtime slice, benchmark or review | Must be reproducible and provenance-linked |
| Maturity | N1–N6 plus P0/P1/P2 and E3/N5 gates | No maturity promotion without the specified gate |
| Claim | Exact permitted statement and audience | Default-deny when passport or gate is incomplete |
| Competitive advantage | Comparative and economic proposition | Prohibited until independent and economic evidence exists |

Every README update is idempotent and PR-governed. The synchronizer updates only the authorised branch, preserves one governed block, excludes forks, records the resulting PR and never writes directly to protected `main`. Recovery uses checkpoints, remote commits and contract artifacts; divergences are reconstructed through a new PR or a named checkpoint, never through destructive history rewriting.

### Pending work register

| Workstream | Current state | Exit condition |
|---|---|---|
| Remote GitHub Security and quality | `BLOCKED` by `security_events` authorization and 403 | Read both main-branch alert tables with an authorized session and record timestamped results |
| Vault provider | `SECURITY_HOLD` with provider-neutral adapter | Approve one backend-only provider and pass rotation/revocation/dual-approval tests |
| Restore and remote diagnostics | `EVIDENCE_REQUIRED` | Complete an isolated restore and a redacted reproducible diagnostic with review |
| External assurance and field evidence | `EVIDENCE_REQUIRED` | Independent S-001 replay, signed review, field KPIs and economic evidence |
| README/plan continuity | PR-governed and recoverable from checkpoints | Merge reviewed PRs only after checks and preserve rollback references |

Open tasks are operational work, not proof of capability. They must remain visible until their exit criteria are met.

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

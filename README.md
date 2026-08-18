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

### Ledger Explorer and governed export

The dashboard now exposes a read-only **Ledger Explorer** for searching commits by full SHA, subject and timestamp, and for filtering the 14 documentary README PRs by status and governed branch. It provides **Interactive commit and PR history** with selected-item detail, while the **Export PDF** action records the current filtered ledger and README/PR state.

The export is an evidence-scoped operational report generated from `CASTUO-COMMIT-LINEAGE.md`, `TRAKY12-README-SYNC-RESULT.json` and the typed `shared/lineageData.ts` projection. It does not expose secrets, alter GitHub state, merge PRs or assert remote Security and quality status. The current lineage contains 57 commits and the governed README surface remains 14/14 PR-governed.

### Complete commit lineage

The complete local commit lineage is reproduced below from the project Git history. A commit records repository history only; it is not, by itself, field evidence, deployment evidence, a security-zero result or a commercial claim.

| # | Commit | Timestamp | Subject |
|---:|---|---|---|
| 1 | 4180ac9bd67f3831b1416d11f15123890f5fc7be | 2026-08-17T16:54:17+00:00 | Initial project bootstrap |
| 2 | df1b84ca7293429504cf0c0d4995e817b9164808 | 2026-08-17T16:58:28+00:00 | Checkpoint: Dashboard CASTÚO-SYSTEM implementado con estética Field Signal Editorial, hero visual, navegación lateral responsive, cadena de evidencia, registro de capacidades filtrable, gates de promoción, estado del CI, notas de campo y assets visuales generados. |
| 3 | d2cbef5b7265b8d2f55abac5b08b62c2c4ed5f5f | 2026-08-17T17:05:03+00:00 | Checkpoint: Segunda iteración del dashboard CASTÚO-SYSTEM: progreso histórico fechado, readout verificable, drawer de detalle por capability, filtros de estado/madurez, CTA contextual y estados CI/bloqueo reflejados. |
| 4 | 5151383b97aef122c8ed45eaad3e8240f422970c | 2026-08-17T17:37:28+00:00 | Checkpoint: Versión web del ecosistema CASTÚO-SYSTEM con mapa interactivo de 16 repositorios, estados CURRENT/SCOPED/PENDING/EXPERIMENTAL/BLOCKED, dashboard de progreso, cadena de evidencia, gates de promoción y estado explícito del CI remoto. |
| 5 | 18fd0c1f07dedbfb2ad5cef2855764f2cf60991d | 2026-08-17T17:41:11+00:00 | Checkpoint: Dashboard interactivo con búsqueda y filtros por estado/progreso del ecosistema, feedback de actualización con estado de sincronización y timestamp, y panel detallado de los seis workflows fallidos de la PR #346 con enlaces de ejecución y límites explícitos de evidencia. |
| 6 | 6792f745ab75d867c93cf18964478ccc788e7dac | 2026-08-17T17:46:12+00:00 | Checkpoint: Dashboard evolutivo con la sección New System Integrations para CASTUO-SYSTEM v6, Quantum/Decision Layer y CASTÚO SaaS Platform; cada artefacto muestra capacidades mapeadas, fuente y riesgo de seguridad, con la plataforma SaaS retenida en SECURITY HOLD hasta mover secretos y APIs a backend. |
| 7 | ebe63480266ddb46ef99943022b8f0255da45d67 | 2026-08-17T17:51:27+00:00 | Checkpoint: Interfaz vault-first para credenciales SaaS sin valores secretos en frontend; simulador Quantum determinista, local y marcado NO CLAIM; indicadores visuales de estado, seguridad, fuente y progreso para CASTUO-SYSTEM v6, Quantum y SaaS; documentación añadida en Castuo-system y Traky12; build de producción validado. |
| 8 | 3a9520a1d5aac6da69637463b14a13f5622df094 | 2026-08-17T18:00:59+00:00 | Checkpoint: Quantum Decision Lab mejorado con barra de Evidence budget, barra de heuristic confidence y gráfico horizontal de Continuity, Assurance y Resources; lecturas deterministas, etiquetadas LOCAL READOUT / NO CLAIM y documentadas en Castuo-system y Traky12; build de producción validado. |
| 9 | 1102ed1e379da6a87df03ba5ebc4ae646fa314ee | 2026-08-17T18:13:18+00:00 | Checkpoint: Upgrade a full-stack con OAuth, tRPC y Drizzle; tablas connector_intents y connector_audit_events; procedimientos protegidos para connect/rotate/revoke con allowlist, scopes mínimos, referencias vault y auditoría redactada; SecurityHoldVaultAdapter provider-neutral; secret scanner y redactor de logs con pruebas; contrato Quantum v1 y paquete de evidencia local reproducible sin evidencia de campo; documentación sincronizada en Castuo-system y Traky12; security scan, TypeScript, 7 tests y build validados. |
| 10 | 6ec553b586612ff04d583aae3c085023ef3fb32d | 2026-08-17T18:15:35+00:00 | Checkpoint: Iteración full-stack final: OAuth/tRPC/Drizzle, intents y auditoría SaaS sin secretos, SecurityHoldVaultAdapter integrado obligatoriamente con AbortSignal.timeout(5000), allowlist y scopes mínimos, redactor de logs general con pruebas, secret scanning, contrato Quantum v1 y paquete de evidencia local reproducible sin evidencia de campo; GitHub core y perfil sincronizados; 9 pruebas, TypeScript, security scan y build validados. |
| 11 | 1d2fb85d64c33f91509f7588f68f4e8728b218dd | 2026-08-17T18:34:16+00:00 | Checkpoint: Manual integral de control SaaS y CASTÚO-SYSTEM; mapa evolutivo por gates con responsables, entradas, salidas y rollback; schema de grants con ownerUserId y versiones de credenciales; endpoints protegidos para grants, revocación, auditoría y versiones; dashboard con estados backend; pruebas de integración para connect/rotate/revoke, permisos, owner isolation, expiración, replay, doble revocación y SECURITY_HOLD; 14 tests, TypeScript, security scan y build validados; documentación sincronizada en Castuo-system y Traky12. |
| 12 | be8b996943523cd1e048d2445594e408f6ae1612 | 2026-08-17T18:49:45+00:00 | Checkpoint: Checkpoint de la iteración de control SaaS: filtros de auditoría por fecha y tipo, exportación CSV de eventos redactados, métricas Quantum de campo y revisión independiente en NO_CLAIM, aprobación dual con ventana de rollback, pruebas de reglas de aprobación, documentación de la línea base Dependabot y sincronización con Castuo-system y Traky12. Las ramas de remediación Dependabot están en 0 local; los branches principales siguen pendientes de aprobación externa y reprocesamiento de GitHub. |
| 13 | 306b798834ee41a755c45f98cd87d0093a1afb11 | 2026-08-17T19:07:59+00:00 | Checkpoint: Checkpoint de cierre técnico parcial: ambas PRs fueron integradas en main con commits f8daa63 y 7d099c8; pnpm audit en ambos main devuelve 0 en todas las severidades; la protección de main fue restaurada en el primer repositorio; se documentó el protocolo remoto y el motivo del 403. La lectura de las tablas Security and quality sigue pendiente porque el token no tiene security_events y la sesión web no está autenticada. |
| 14 | 195bd883e09786b8de70bd43ff7f7d59232604ba | 2026-08-17T19:20:52+00:00 | Checkpoint: Checkpoint de External Assurance: CAP-ASSURANCE-001, estructura de Due Diligence Evidence Pack, plantilla Capability Trust Passport, GATE-R1, G-COMM, negative evidence, Assurance Profile visible en dashboard, documentación sincronizada en Castuo-system y Traky12, prueba específica del contrato y validación completa con 19 tests, TypeScript, secret scan y build. La verificación remota de Dependabot continúa pendiente por el 403 de seguridad. |
| 15 | ffcf568a9fc807bc18a2b94c460ca3f820a26507 | 2026-08-17T19:29:20+00:00 | Checkpoint: Checkpoint de integración pública: contrato tipado del Public Knowledge & Evidence Index con 29 registros sobre 14 superficies, estados EVIDENCE-SCOPED/STAGING-CANDIDATE/PROMOTION-BLOCKED, referencias cruzadas explícitas a Secure Connectors, Evidence Passport, Capability Trust Passport y gates/negative evidence, filtros de búsqueda por estado, prueba de no elevación de claims y exclusión de secretos, contrato documental sincronizado con Castuo-system y Traky12, y validación de 21 tests, TypeScript, security scan, build y responsive desktop/móvil. Permanecen pendientes únicamente las consultas remotas de Security and quality bloqueadas por 403. |
| 16 | 4946e123db66589fbd8d576cea22e3bff84fba11 | 2026-08-17T19:47:18+00:00 | Checkpoint: Checkpoint de remediación y P1: dependency scan local en 0 advisories mediante override scoped express>path-to-regexp 0.1.13 compatible con Express 4; secret scan, SBOM, TypeScript, 28 pruebas y build validados; catálogo P1 de sensibilidad para 16 repositorios; observabilidad runtime de conectores con métricas, p95, trazas redactadas y alertas reproducibles; dashboard y documentación sincronizados en Castuo-system y Traky12; permanecen bloqueos externos GitHub 403 y SECURITY_HOLD del vault. |
| 17 | f07057b01de9c338ad86b756eebf4ecb098ace32 | 2026-08-17T19:51:55+00:00 | Checkpoint: Checkpoint de assurance P1 ampliado: schema Evidence/Trust Passport aplicado al template real con sensitivity, provenance, audience, retention y redaction; política default-deny y pruebas contra artefacto real; contrato local backup/restore con SHA-256, envelope versionado, auditoría y detección de manipulación; 32 pruebas y TypeScript validados; sincronización realizada con Castuo-system y Traky12; siguen pendientes la restauración efímera real, diagnóstico remoto GitHub 403, vault real, evidencia de campo y claims P2. |
| 18 | 148404af6fcdcb2dd197b1188c2d1610df41d09f | 2026-08-17T19:55:00+00:00 | Checkpoint: Checkpoint de continuidad: gate de selección vault con cuatro candidatos backend-only en SECURITY_HOLD y aprobación dual; AI Security Passport default-deny con provenance, límites de datos, permisos de herramientas, evaluación y claims prohibidos; contrato local checksum backup/restore; schema completo de Trust Passport y política de redacción; 35 pruebas, TypeScript, secret scan, dependency scan en 0 advisories, SBOM y build validados; sincronizado en Castuo-system y Traky12. Pendientes reales: proveedor vault aprobado, GitHub Security and quality/checks con sesión autorizada, restore efímero remoto, evidencia de campo y claims comerciales. |
| 19 | e7e6c7464a7775d06e103e10a59d431fdb5e0f81 | 2026-08-17T19:56:49+00:00 | Checkpoint: Checkpoint UI y assurance: dashboard muestra el Vault Provider Gate con cuatro candidatos, SECURITY_HOLD, backend-only y aprobación dual; P1 sensibilidad, observabilidad runtime, schema Trust Passport, política de redacción, backup/restore checksum y AI Security Passport sincronizados; 35 pruebas, TypeScript, secret scan, dependency scan en 0 advisories, SBOM, build y responsive verificados. Siguen pendientes sólo acciones que requieren autorización o evidencia externa: proveedor vault aprobado, GitHub Security and quality/checks, restore efímero remoto, campo y comercial. |
| 20 | 020e823eeef58fdb321266a40851aacba2d375c2 | 2026-08-17T20:09:10+00:00 | Checkpoint: Checkpoint del estudio competitivo aprobado: investigación primaria de Credo AI, IBM watsonx.governance, Fiddler AI, Microsoft Purview, ServiceNow AI Control Tower y Palantir Ontology; matriz de 11 registros y 7 ejes con estados 1/0/?/N/A y escenarios Balanced, Evidence-first, Field-first y Enterprise-first; Competitive Capability Passports persistidos con capabilityStates, allowedClaims, forbiddenClaims, provenance, madurez y límites; informe Markdown, notas de investigación, pruebas contractuales, dashboard integrado y sincronización a Castuo-system y Traky12. Validado con 42 tests, TypeScript, secret scan, dependency scan en 0 y build. |
| 21 | 23420885f0e651b5024834c7ac8ee63ed0a7a962 | 2026-08-17T20:12:18+00:00 | Checkpoint: Checkpoint de estudio competitivo ampliado: matriz binaria 1/0/?/N/A con 17 registros y 7 ejes; fuentes primarias verificadas de Credo AI, IBM, Fiddler, Microsoft Purview, ServiceNow, Palantir, Vidimus, Hydrus, Praxedo y Nomadia; seis hipótesis europeas conservadas como UNVERIFIED; 17 Competitive Capability Passports persistidos con capabilityStates, allowedClaims, forbiddenClaims, provenance, madurez y siguiente verificación; informe, notas de investigación, dashboard y pruebas sincronizados en Castuo-system y Traky12. Validación: 42 tests, TypeScript, secret scan, dependency scan en 0 advisories y build. |
| 22 | cc56350ff8d4f57c47b883512172f04a0e0810c4 | 2026-08-17T20:14:14+00:00 | Checkpoint: Checkpoint de la matriz competitiva binaria ampliada: 17 records, 10 fuentes primarias verificadas, seis hipótesis europeas conservadas como UNVERIFIED, 17 Competitive Capability Passports completos con estados binarios y claims prohibidos, filtros de región/estado de evidencia en el dashboard, investigación y UI sincronizadas con Castuo-system y Traky12. Validación de esta iteración: 42 tests, TypeScript, secret scan, dependency scan en 0 advisories y build. |
| 23 | a8b31b00162fc4930de7671fa8cd0a085a72049c | 2026-08-17T20:15:52+00:00 | Checkpoint: Checkpoint P2: protocolo documentado para segunda implementación, benchmark multi-adapter, AI Security Passport, revisión externa, field validation y evidencia comercial; default-deny explícito y sin elevar claims de producción. Añadida prueba contractual del documento. Validado con 43 tests, TypeScript, secret scan y build; sincronizado en Castuo-system y Traky12. Pendientes siguen siendo la prueba real de restore/diagnóstico remoto, vault real y assurance remoto. |
| 24 | 1d9cfa4d7ee4bd166c155a94991717f1610a58f1 | 2026-08-17T20:20:31+00:00 | Checkpoint: Checkpoint de scoring competitivo: el escenario seleccionado calcula `coverage proven` sólo sobre estados conocidos 1/0, separa `evidence completeness`, mantiene `?` como incertidumbre y excluye N/A del denominador; la tabla muestra ambas lecturas y el unknown weight. Añadidos helper compartido y pruebas comparativas ? versus 0. Validado con 46 tests, TypeScript, secret scan, dependency scan en 0 advisories y build; sincronizado en Castuo-system y Traky12. |
| 25 | d14671f57f9f5b79c6c5d0c55e6ac0aaf74962ae | 2026-08-17T20:23:31+00:00 | Checkpoint: Checkpoint P1 local: smoke test real sobre filesystem temporal con SHA-256, restore byte-a-byte y tamper boundary; contrato de diagnóstico redacted con gate states, claim boundary y campos prohibidos sin valores sensibles; documentación P1 actualizada y sincronizada en Castuo-system y Traky12. Validación completa: 47 tests, TypeScript, secret scan, dependency scan en 0 advisories, smoke y build. El restore de producción, diagnóstico remoto, vault real y assurance remoto permanecen pendientes. |
| 26 | 1082664b53e67352c0e08fd95e6d2569d32b7259 | 2026-08-17T20:42:14+00:00 | Checkpoint: Checkpoint S-001 final: contrato del Competitive Reproducibility Benchmark con semántica 1D/1V/1R, fixture canónico, métricas deterministas, gates P2→E3→N5 y separación explícita entre capability, evidence, maturity, claim y competitive advantage. Dashboard con readout local, madurez y límites; 17 Competitive Capability Passports persistidos enlazados a S-001; documentación y pruebas sincronizadas con Castuo-system y Traky12. Validado con TypeScript, 55 tests, secret scan, dependency scan en 0 advisories y build. |
| 27 | 882373f5ca93713d79bbafd4092e4666c5c35ee2 | 2026-08-17T20:57:05+00:00 | Checkpoint: Checkpoint de integración del perfil Traky12: 16 repositorios remotos inventariados con README, sensibilidad y estados de evidencia; 14 superficies propias actualizadas mediante PRs auditables, incluidos Traky12/Traky12#8, con forks excluidos y cero escrituras directas en main; bloque README común con arquitectura de tres planos, S-001, semántica 1D/1V/1R y límites de claims; mapa de trazabilidad completo; artefactos y pruebas sincronizados en Castuo-system commit ad567a4 y Traky12 management commit 4e8d336. Validado con 58 tests, TypeScript, secret scan, dependency scan en 0 advisories, enlaces GitHub alcanzables y build verde. |
| 28 | 2d2dcde8c067c70d356df1fbadcecfb275743fb4 | 2026-08-17T20:59:15+00:00 | Checkpoint: Checkpoint posterior a la integración del perfil Traky12: inventario remoto de 16 repositorios con sensibilidad y evidencia; bloque README gobernado; mapa de trazabilidad completo; artefacto único de 14 PRs abiertas incluyendo Traky12/Traky12#8; validación remota de URLs y estados; registro OPEN-EXTERNAL-GATES con criterios de salida y rollback; artefactos sincronizados en Castuo-system commit f6ab466 y Traky12 management commit 49e80bd. Gates locales: 59 tests, TypeScript, secret scan, dependency scan 0 advisories. Permanecen abiertos sólo controles que requieren GitHub security_events, proveedor vault aprobado, restore de producción, diagnóstico remoto y evidencia externa. |
| 29 | a08bf2491eecbe161d863d5a86c4f9a937670921 | 2026-08-17T21:05:33+00:00 | Checkpoint: Checkpoint de actualización integral de README: bloque común ampliado con progreso SaaS vault-first, Quantum, P0/P1/P2, Competitive Study, S-001, passports, scoring, trazabilidad y gates abiertos; 14 ramas PR autorizadas actualizadas, 14/14 README remotos verificados con marcadores únicos, contenidos completos, sin duplicados ni claims positivos prohibidos; forks excluidos y main sin escrituras directas. Artefactos resincronizados en Castuo-system commit 41b05fd y Traky12 management commit 33f94b4. Gates locales mantienen 59 tests, TypeScript, secret scan, dependency scan 0 advisories y build verde. |
| 30 | 2ac29bf6732bacf34b8274e4eac0e23f42d1e81d | 2026-08-17T21:15:25+00:00 | Checkpoint: Checkpoint de integración completa de Castuo-system: se añadió CASTUO-SYSTEM-OPERATING-INDEX.md con arquitectura de tres planos, tareas, P0/P1/P2, S-001, semántica de claims, gates, trazabilidad y estado GitHub; se sincronizó en la PR #347 y management branch; se amplió el bloque README con enlace al índice y se resincronizaron 14 PRs. Validación: 59 tests, TypeScript sin errores, secret scan pasado, dependency scan con 0 advisories locales, SBOM, build y validación remota 14/14. Permanecen bloqueados por autorización/evidencia externa: review/merge de PRs, GitHub security_events/403, vault real, restore/assurance remotos y P2 de campo/economía. |
| 31 | c4d99e0d0f282bc83346cdad620074504f900c89 | 2026-08-17T21:23:21+00:00 | Checkpoint: Checkpoint de confirmación integral: inventario remoto revalidado con 16 repositorios, 14 superficies propias y 2 forks excluidos; 14 PRs abiertas con cero escrituras directas en main; validador reforzado para comprobar explícitamente el enlace `CASTUO-SYSTEM-OPERATING-INDEX.md`, resultado remoto 14/14; mapa de trazabilidad 16/16; dashboard revalidado con 59 tests, TypeScript, secret scan, dependency scan 0 advisories locales, SBOM y build; rutas `/quantum` y `/secure-connectors` corregidas y verificadas en móvil; OPEN-EXTERNAL-GATES actualizado sin elevar claims. Siguen abiertos GitHub 403/security_events, vault real, restore/diagnóstico remoto, assurance independiente y field/economic evidence. |
| 32 | 24af3c712c82b01df6c821024336dcc1bac7e68d | 2026-08-17T21:25:46+00:00 | Checkpoint: Checkpoint de confirmación ampliada: 14/14 README PRs revalidados con enlace explícito al índice operativo; se añadió prueba contractual de regresión, elevando la suite a 60 tests; 16/16 inventario y trazas; rutas profundas del dashboard sin 404; OPEN-EXTERNAL-GATES actualizado y sincronizado en Castuo-system y Traky12 management; TypeScript, secret scan, dependency scan 0 advisories locales, SBOM y build correctos. Gates externos permanecen abiertos: GitHub security_events/403, vault real, restore/diagnóstico remoto, assurance independiente y validación field/económica. |
| 33 | cb02a495551f37e63e241785a1ee5caf0e4627bf | 2026-08-17T21:27:11+00:00 | Checkpoint: Checkpoint de continuación: validación remota 14/14 de README con enlace explícito al índice, 16/16 inventario y trazabilidad, 60 tests con prueba contractual de enlaces, TypeScript, secret scan, dependency scan 0 advisories locales, SBOM, build y rutas profundas sin 404. OPEN-EXTERNAL-GATES actualizado con diagnóstico HTTP 403 y alcance GitHub aceptado `security_events`, sincronizado y verificado en Castuo-system PR branch y Traky12 management branch. No se registran tokens ni se cierran gates externos. |
| 34 | 21c302bfd89e515aaa01cea343ac6f763cd38760 | 2026-08-17T21:33:24+00:00 | Checkpoint: Checkpoint de recuperación y refuerzo: la auditoría confirmó que HEAD local cb02a49 y los artefactos críticos estaban recuperables; se reforzó el bloque común README con registro de tareas pendientes, continuidad de commits y criterios de salida; se actualizó el índice operativo; se resincronizaron las 14 PRs autorizadas y se validaron remotamente 14/14, con cero escrituras directas en main; Castuo-system PR #347 contiene README, índice y OPEN-EXTERNAL-GATES. Validación local: 60 tests, TypeScript, secret scan, dependency scan 0 advisories, SBOM, governance validation y build. Los gates GitHub security_events/403, vault real, restore/diagnóstico remoto y evidencia externa permanecen abiertos. |
| 35 | 87236f6849a2dc56c20409d1bb2677334568fbff | 2026-08-17T21:35:03+00:00 | Checkpoint: Checkpoint de recuperación reforzada: estado local cb02a49 y artefactos críticos recuperados; índice operativo ampliado con continuidad de commits, comparación de fuentes y tareas abiertas; bloque README reforzado con Pending work register y criterios de salida; 14 PRs resincronizadas y validadas 14/14 sin escrituras directas en main; validador y prueba contractual exigen índice y registro de tareas; 60 tests, TypeScript, secret scan, dependency scan 0 advisories, SBOM, governance validation y build correctos. Bloqueos honestos: GitHub security_events/403, merge/reviews, vault real, restore/diagnóstico remoto y evidencia independiente/field/económica. |
| 36 | 6ec3a17f36069d4db04aacd137df5155d67796ce | 2026-08-17T21:37:09+00:00 | Checkpoint: Checkpoint de continuidad reforzada: se añadió `CASTUO-RECOVERY-MANIFEST.json` con schema, HEAD local, checkpoint, PR #347, 11 hashes de artefactos críticos, conteos 14/14 y claim boundary sin secretos; se sincronizó y verificó en Castuo-system y Traky12 management; el índice operativo fue actualizado para referenciar el manifiesto; 14 README PRs siguen resincronizadas y validadas; 60 tests, TypeScript, scans, SBOM, governance validation y build verdes. Persisten únicamente gates externos que requieren autorización o evidencia: GitHub security_events/403, reviews/merge, vault real, restore/diagnóstico remoto y assurance/field/economic evidence. |
| 37 | e150c094c7e31fdc19e0fc11e981876a4532533a | 2026-08-17T21:40:56+00:00 | Checkpoint: Checkpoint de auditoría de continuidad: se generó `TRAKY12-PR-STATUS-AUDIT.json` con 14 PRs abiertas, ramas base/head, mergeability, decisiones de revisión, checks visibles cuando están disponibles y `NOT_VERIFIED / 403` para Security and quality; el artefacto fue sincronizado en Castuo-system y Traky12 management; el índice operativo lo referencia; 14 README siguen validados, 60 tests y TypeScript verdes. Persisten gates externos sin cierre por permisos/revisión/evidencia, no por pérdida de commits. |
| 38 | f723d3158aca8540b6066d4d4277984d26ea4c73 | 2026-08-17T21:42:38+00:00 | Checkpoint: Checkpoint de consolidación: se creó y sincronizó `EXTERNAL-GATE-EXECUTION-PACK.md` con procedimientos seguros, criterios de salida, evidencia y rollback para GitHub Security and quality, vault, restore/diagnóstico y assurance/field; el índice operativo lo referencia en Castuo-system y Traky12 management; siguen vigentes auditoría 14 PRs, manifiesto de recuperación y validación 14/14; 60 tests y TypeScript verdes. No se cierran gates externos ni se registran secretos. |
| 39 | f4bc081fde5d5fc28481722dc6073bc5728d0ac6 | 2026-08-17T21:51:11+00:00 | Checkpoint: Checkpoint de transcripción integral: el bloque README ahora incluye Full operating plan transcription, backlog operativo, recuperación de commits, matriz Capability/Evidence/Maturity/Claim/Competitive Advantage, reglas de sincronización PR-governed, gates y límites de claims; se propagó a 14 PRs autorizadas sin escrituras directas en main; validación remota 14/14 sin faltantes ni claims prohibidos; 60 tests, TypeScript, secret scan, dependency scan 0 advisories, SBOM, governance validation y build correctos. Los gates externos continúan documentados como bloqueados o pendientes. |
| 40 | 4cd2dce068a332a0dde66d4f5cd6b54ad73b1fdb | 2026-08-17T21:59:28+00:00 | Checkpoint: Checkpoint de arquitectura soberana: se creó y sincronizó `CASTUO-SOVEREIGN-REFERENCE-ARCHITECTURE.md` con jerarquía canónica de autoridad, ownership, soberanía de datos, commit lineage, control de cambios y rollback; el bloque README y el índice operativo lo referencian; se propagó a las 14 PRs autorizadas sin escrituras directas en main; validador exige la referencia soberana; 14/14 README válidos, sin claims prohibidos, 60 tests, TypeScript, secret scan, dependency scan 0 advisories, SBOM, governance validation y build correctos. Los gates externos permanecen abiertos por autorización/evidencia requerida. |
| 41 | 4dd5554c9fd66fa59667ea2e6f03ebf558db5745 | 2026-08-17T22:00:34+00:00 | Checkpoint: Checkpoint de gobernanza reforzada: arquitectura soberana documentada y sincronizada en Castuo-system y Traky12, README/índice actualizados y 14/14 validados; se añadió contrato local para proteger jerarquía de autoridad, ownership, commit lineage, rollback y claim boundary; la suite queda en 61 tests verdes y TypeScript correcto. Los gates externos siguen abiertos, explícitos y sin claims promovidos. |
| 42 | 799a3a67094cd788bb13cb58ae401d7b5e2445e0 | 2026-08-17T22:03:53+00:00 | Checkpoint: Checkpoint de gobernanza de cambios: se añadió `CASTUO-COMMIT-GOVERNANCE-POLICY.json` con requisitos de commits, PRs, ownership, checks, claim policy y rollback; se sincronizó en Castuo-system y Traky12 management; README e índice operativo lo referencian; validador exige la referencia en 14/14 README; 61 tests y TypeScript correctos. Los gates externos permanecen abiertos y separados de la validación local. |
| 43 | 964369883e9051d6023ee38ace369e3249452a82 | 2026-08-17T22:05:01+00:00 | Checkpoint: Checkpoint de integración soberana validada: 14/14 README contienen arquitectura soberana y política machine-readable de commits; Castuo-system y Traky12 management contienen los artefactos canónicos; PR audit registra 14/14 abiertas y 0 escrituras directas en main; validación sin faltantes ni claims prohibidos; 61 tests verdes, TypeScript correcto, scans/SBOM/governance correctos y build de producción correcto. Los gates externos permanecen abiertos por autorización/evidencia, sin promoción de claims. |
| 44 | d175eab982059327eb5054399ff1182b18bdf467 | 2026-08-17T22:10:18+00:00 | Checkpoint: Checkpoint del programa de madurez: estrategia adjunta formalizada como `CASTUO-MATURITY-ACCELERATION-PROGRAM.md` con orden seguridad→CI→vertical slice→observabilidad/restore→E3→piloto→mercado, frentes P0/P1/P2/E3/G-COMM, control plane canónico, S-001, evidence strength E0–E6, límites N3/N4/N5/N6, roadmap temporal, KPI, ECR y Promotion Debt; README e índice lo referencian; 14 PRs sincronizadas y validadas 14/14 sin claims prohibidos; 61 tests, TypeScript, secret scan, dependency scan 0 advisories, SBOM, governance y build correctos. |
| 45 | 476d8b6de8aa65860858f96e97b7ae21a8608bd5 | 2026-08-17T22:23:08+00:00 | Checkpoint: Checkpoint de narrativa pública: se creó `CASTUO-PUBLIC-NARRATIVE-AND-WEDGE.md` con posicionamiento de CASTÚO-SYSTEM como evidence-governed control plane, título profesional, wedge `Evidence-Ready Field Operations`, baseline público Traky12, modelo de un sistema modular, secuencia de confianza y límites de claims. README e índice lo referencian; 14 PRs sincronizadas y validadas 14/14 sin faltantes ni claims comparativos positivos; 61 tests verdes y TypeScript correcto. |
| 46 | bd756a328248d632ee4a0122aabc6fda766737aa | 2026-08-17T22:37:53+00:00 | Checkpoint: Checkpoint de reputación pública: auditoría fechada del perfil Traky12 y repositorio faro; estrategia `CASTUO-OSS-REPUTATION-STRATEGY.md` integrada con posicionamiento profesional, contribuciones útiles, colaboración real, Discussions técnicas, documentación, releases y tracción orgánica; prohibición explícita de PRs triviales, Discussions artificiales, cuentas espejo, actividad inflada y estrellas sintéticas; README e índice sincronizados en Castuo-system y Traky12 management; validador 14/14 sin faltantes ni forbidden claims; 61 tests verdes y TypeScript correcto. |
| 47 | 0e04560a3ff78d85c0eed58b6142e231f4820383 | 2026-08-17T23:09:07+00:00 | Checkpoint: Checkpoint de integración de los documentos adjuntos: creado `CASTUO-INTEGRAL-IMPROVEMENT-AND-SOVEREIGN-STATE.md` con evolución del ecosistema al control plane, arquitectura modular, evidence/claim discipline, seguridad backend-only/vault, maturidad G0→N6, matriz competitiva, reputación OSS, continuidad soberana y gates pendientes. README e índice actualizados y sincronizados; 14/14 PRs válidas, sin faltantes ni claims prohibidos; 61 tests, TypeScript, contracts y build locales correctos. |
| 48 | 01264ad6906d7f5a9b4dc56d97176fbb25d49be3 | 2026-08-17T23:22:17+00:00 | Checkpoint: Checkpoint de cierre integral: backlog global auditado; contrato de completitud de artefactos canónicos añadido; 14/14 README/PRs, sin faltantes ni forbidden claims; 62 tests verdes; TypeScript, secret scan, dependency scan local con 0 advisories, SBOM, governance y build correctos; OPEN-EXTERNAL-GATES actualizado con criterios de cierre para Security and quality remoto, vault, assurance, restore/diagnóstico y evidencia field/economic. No se promueven claims externos no verificados. |
| 49 | 8c341f45b929fd225d5b8f4f5f0a0ca8804f870f | 2026-08-17T23:40:29+00:00 | Checkpoint: Checkpoint de continuidad del plan completo: backlog reauditado; refuerzos locales y evidencia de cierre preparados; README, índice, gates y recovery manifest resincronizados; 14/14 README/PRs válidas, sin faltantes ni forbidden claims; 62 tests verdes; TypeScript, secret scan, dependency scan local 0 advisories, SBOM, governance y build correctos. Los gates externos —Security and quality remoto, security_events, vault real, assurance, restore/diagnóstico y evidencia field/economic— permanecen abiertos con criterios de cierre documentados. |
| 50 | c32951edd616ee5c425c74fd6c7172bc4a74f0f1 | 2026-08-17T23:57:44+00:00 | Checkpoint: Checkpoint de exportación GitHub: auditoría de ramas y PRs completada; 21 artefactos canónicos preparados y 42 actualizaciones/creaciones exportadas a las dos ramas gobernadas; bloque README sincronizado y validado 14/14; PR #347 y las 14 PRs permanecen abiertas sin escrituras directas en main; 62 tests, TypeScript, secret/dependency scans, SBOM, governance y build correctos; estado remoto bloqueado sólo por revisión/permisos y gates externos documentados. |
| 51 | be1938b211a710bdfad37a948b48e1da00a72f45 | 2026-08-18T00:03:55+00:00 | Checkpoint: Checkpoint de continuidad GitHub: exportación de 21 artefactos y README 14/14 preservada; diagnóstico de autorización actualizado con la respuesta HTTP 403 del 2026-08-18, sin tokens expuestos, y sincronizado en Castuo-system y Traky12 management. Se mantienen 62 tests, TypeScript, scans, SBOM, governance y build correctos; Security and quality remoto sigue `BLOCKED / NOT_VERIFIED` hasta autorizar `security_events`. |
| 52 | 7226fdb33df4c9b421393de95cf5e0ab81393d55 | 2026-08-18T00:29:49+00:00 | Checkpoint: Checkpoint de continuidad del plan: 28 archivos de prueba y 62 tests verdes; TypeScript y build correctos; gobernanza remota 14/14 README válida sin claims prohibidos; índice operativo actualizado con checkpoint `be1938b2` y diagnóstico GitHub 403 del 2026-08-18; cambios sincronizados en Castuo-system y Traky12 management. Permanecen abiertos únicamente los gates que requieren `security_events`, proveedor vault aprobado, assurance remota y evidencia real de restore/campo. |
| 53 | 874934fbf1b8cebc389a491232de0dfced6f4983 | 2026-08-18T00:31:01+00:00 | Checkpoint: Checkpoint de reauditoría externa: la lectura de Security and quality se reintentó en ambos repositorios objetivo y ambos endpoints devolvieron HTTP 403; el resultado se documentó y sincronizó en Castuo-system y Traky12 management. La validación local conserva 62 tests verdes, TypeScript, build y gobernanza README 14/14. No se afirma cero alertas remotas ni cierre de vault, assurance o restore. |
| 54 | f2f87c4ec6fef84c4f6a377ec3af79ee00093aa0 | 2026-08-18T00:33:47+00:00 | Checkpoint: Checkpoint de cierre local: 28 archivos y 62 tests verdes; TypeScript, build, secret scan sin hallazgos, dependency scan con 0 advisories, SBOM local generado, validación documental y render visual correctos. El índice operativo documenta el alcance local y mantiene sin cerrar los gates de GitHub remoto, vault real, assurance y restore/producción. |
| 55 | 4735e8102ca721132f6546b9265cbf51c21a604d | 2026-08-18T00:49:01+00:00 | Checkpoint: Checkpoint de integración de lineage: se generó `CASTUO-COMMIT-LINEAGE.md` con 54 commits locales y se reprodujeron todos sus SHA dentro del bloque README gobernado; el bloque se sincronizó en 14 PRs nuevas de la rama `docs/castuo-governed-readme-20260818`, sin escrituras directas en main. Se añadió contrato de lineage, la suite queda en 64 tests verdes, TypeScript/build/scans/SBOM correctos y el índice operativo referencia el ledger. Los gates remotos continúan sin promoción. |
| 56 | bf62f01e54700ebef9ef8a3ab13f8914c0b4da97 | 2026-08-18T00:49:55+00:00 | Checkpoint: Checkpoint de integración completa de README: 54 commits locales registrados en `CASTUO-COMMIT-LINEAGE.md` y reproducidos en el bloque README; 14 PRs abiertas en `docs/castuo-governed-readme-20260818`, 0 escrituras directas en main, 14/14 README validados sin claims prohibidos. Se añadió prueba contractual de lineage; 64 tests verdes, TypeScript, build, secret scan, dependency scan y SBOM correctos. Los gates externos permanecen documentados sin promoción. |
| 57 | 0a7e510b9cafb502a44170ea49fa43a4dc19d00b | 2026-08-18T00:54:22+00:00 | Checkpoint: Checkpoint de continuidad de lineage: el historial actual contiene 56 commits y `CASTUO-COMMIT-LINEAGE.md` fue regenerado; el bloque README reproduce los 56 SHA y se resincronizó en 14 PRs de `docs/castuo-governed-readme-20260818`. Validación: 14/14 README correctos, sin faltantes ni claims prohibidos, 64 tests verdes y TypeScript correcto. No se modificaron ramas main ni se promovieron gates remotos. |
| 58 | 9d1711a3acca49a05074a425432593658549abd4 | 2026-08-18T01:10:27+00:00 | Checkpoint: Checkpoint de continuidad README: el historial actual contiene 57 commits; `CASTUO-COMMIT-LINEAGE.md` y el bloque README fueron regenerados para incluir todos los SHA, incluido `0a7e510b`. Las 14 PRs autorizadas de `docs/castuo-governed-readme-20260818` están sincronizadas, 14/14 README validados sin faltantes ni claims prohibidos, 64 tests verdes y TypeScript correcto. No se modificaron ramas main ni se promovieron gates externos. |
| 59 | 0981a2a17809a36f7f3876edfd80bbd7cd19f4f2 | 2026-08-18T01:34:45+00:00 | Checkpoint: Checkpoint de Ledger Explorer: se añadió búsqueda por SHA/mensaje/repositorio/PR, filtros de estado y rama, historial interactivo de 57 commits y 14 PRs, detalle seleccionado y exportación PDF del estado filtrado del ledger/README con jsPDF. Se añadieron datos tipados reproducibles, contrato de lineage Explorer y validador README reforzado. Validación: 30 archivos y 66 tests verdes, TypeScript, build, secret scan sin hallazgos, dependency scan 0 advisories, SBOM de 88 componentes, render desktop/móvil verificado; 14/14 README gobernados válidos. Gates externos no promovidos. |
| 60 | adc86618288b42e2599fe0a9ca7a00dd19914934 | 2026-08-18T01:36:21+00:00 | Checkpoint: Checkpoint de continuidad Ledger Explorer: búsqueda y filtros de commits/PRs, panel interactivo, detalle seleccionado y exportación PDF implementados. El ledger fue regenerado a 59 commits actuales, proyectado en `shared/lineageData.ts` y sincronizado en 14 PRs README; validador reforzado: 14/14 correctas, sin faltantes ni claims prohibidos. Validación local: 30 archivos y 66 tests verdes, TypeScript, build, secret scan, dependency scan 0 advisories, SBOM 88 componentes y responsive verificado. No se modificó main ni se promovieron gates externos. |

The generated source artifact is docs/governance/CASTUO-COMMIT-LINEAGE.md. Its timestamp is informational; the commit SHA and subject are the auditable fields.

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

### Binary Value Rule v1.0

CASTÚO uses a strict 0/1 promotion rule: a condition is `1` only when primary, traceable and reproducible evidence exists within the declared scope; there is no 0.5 for nearly complete work. The current conservative readout is **3/12**: B01 Architecture defined, B02 Capability implemented and B03 Local reproducible test are `1`; B04–B12 remain `0` because remote CI, independent replay, runtime, observability, field, vendor, vault and commercial evidence are not yet verified.

| Level | Critical binaries | State | Result |
|---|---|---|---|
| A / existence | B01+B02+B03 | OPEN | Exists and reproduces locally |
| B / verifiability | B04+B05 | BLOCKED | Remote observation and independent replay required |
| C / operation | B06+B07+B10 | BLOCKED | Runtime, observability and operational security required |
| D / field | B08+B09 | BLOCKED | Field validation and vendor independence required |
| E / business | B11+B12 | BLOCKED | Paid pilot and transferability required |

The immediate critical sequence is `B04 → B05`. A README, planned task, architecture or local test cannot be used to claim remote CI, production runtime, zero remote alerts, field validation, vendor independence, commercial proof or competitive advantage. See [`CASTUO-BINARY-VALUE-RULE.md`](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/CASTUO-BINARY-VALUE-RULE.md) for the canonical matrix, evidence requirements, blockers and rollback boundary.
<!-- CASTUO-GOVERNED-README-BLOCK:END -->

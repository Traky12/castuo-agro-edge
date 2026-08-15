# CASTÚO-SYSTEM™ — Architecture governance scope

## Repository role

- **Role:** EDGE
- **Function:** Offline-first, MQTT, sensores y gateway
- **Repository visibility:** PUBLIC
- **Control plane:** [`castuo-evolution`](https://github.com/Traky12/castuo-evolution)
- **Public evidence index:** [`Traky12/Traky12`](https://github.com/Traky12/Traky12)
- **Evidence Center:** [`evidence-center`](https://github.com/Traky12/Traky12/tree/main/evidence-center)

## Current truth boundary

El piloto de campo requiere datos, baseline y autorización verificables.

A README, template, fork, commit or green workflow is evidence of an artifact or test within its scope. It is not automatically proof of certification, legal conformity, production operation, customer contract, funding, cash receipt or commercial success.

## Required evidence envelope

Every promoted capability must identify: repository, commit/tag, environment, owner, policy version, protocol, baseline, KPI definitions, raw results, artifact hashes, reviewer, decision and reassessment triggers.

## Minimum states

`DOCUMENTED` → `IMPLEMENTED` → `TESTED` → `VALIDATED` → `PILOT` → `OPERATIONAL`

A model, provider, key, tenant, schema, dataset, chain or environment change activates `REASSESSMENT_REQUIRED`.

## Security baseline

Secrets remain outside Git. Public artifacts contain no credentials or unnecessary personal data. Inputs are validated, access is least-privilege, TLS and encryption-at-rest are configured by environment, device identities are revocable, logs avoid secrets, and backups have a restoration test.

## Promotion Gate

No capability is promoted without a reproducible test and evidence appropriate to its state. Negative results are retained as findings and followed by remediation and re-test.

# CASTÚO-SYSTEM integration boundary

This repository is part of the CASTÚO-SYSTEM ecosystem and receives an adaptation of the binary evolution architecture. The canonical capability is `S-001A` — evidence-preserving local continuity under connectivity loss.

The integration preserves these states: `VALIDATED_LOCAL`, `EVIDENCE_SCOPED`, `HUMAN_REVIEW_PENDING`, `EXTERNAL_VERIFICATION_PENDING`, `PROMOTION_BLOCKED` and `NOT_CLAIMED`. Local execution never implies production, field, N5/N6, federation, provider independence or full sovereignty.

The promotion predicate is conjunctive:

```text
PROMOTE = capability ∧ evidence ∧ replay ∧ security
          ∧ sovereignty ∧ resilience ∧ review ∧ rollback
```

Any unknown, pending or failed mandatory state remains blocking. Private keys, secrets, credentials, PII and production payloads are excluded from this integration.

## Common references

- Canonical contract: `CAP-S001A-OFFLINE-CONTINUITY`.
- Evidence scenario: `S-001A`.
- Current claim boundary: `LOCAL_RESULT_NO_CLAIM`.
- Next gate: independent review, trusted signature ceremony and authorized representative rollback.

## Repository role

**Role:** `edge`
**Description:** Offline-first edge and IoT runtime, buffering and telemetry continuity.

This repository must implement only the controls applicable to this boundary and must link its evidence to a commit or tag.

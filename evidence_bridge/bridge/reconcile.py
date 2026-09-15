"""Reconcile ingested events: duplicate detection, sequence gaps, delayed arrivals.

STATUS: NOT_IMPLEMENTED — EB-POC-001 iteration 2.
See docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md for the scope cut.
"""

from typing import Iterable


def reconcile(events: Iterable[dict]) -> dict:
    return {
        "status": "not_implemented",
        "reason": "EB-POC-001 iteration 2 — see docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md",
    }

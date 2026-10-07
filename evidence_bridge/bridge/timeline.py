"""Build a deviation timeline: event -> alert -> observation -> action -> QMS reference -> outcome.

STATUS: NOT_IMPLEMENTED — EB-POC-001 iteration 2.
See docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md for the scope cut.
"""

from typing import Iterable


def build_timeline(deviation: dict, events: Iterable[dict], actions: Iterable[dict]) -> dict:
    return {
        "status": "not_implemented",
        "reason": "EB-POC-001 iteration 2 — see docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md",
    }

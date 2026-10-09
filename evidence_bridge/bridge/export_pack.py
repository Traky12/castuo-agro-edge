"""Export a versioned Evidence Pack (manifest + timeline) for human review.

STATUS: NOT_IMPLEMENTED — EB-POC-001 iteration 2.
See docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md for the scope cut.
"""

from pathlib import Path
from typing import Iterable


def export_pack(events: Iterable[dict], output_dir: Path) -> dict:
    return {
        "status": "not_implemented",
        "reason": "EB-POC-001 iteration 2 — see docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md",
    }

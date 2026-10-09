"""Independently re-verify an exported Evidence Pack's hashes without trusting the exporter.

STATUS: NOT_IMPLEMENTED — EB-POC-001 iteration 2.
See docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md for the scope cut.
"""

from pathlib import Path


def verify_pack(pack_dir: Path) -> dict:
    return {
        "status": "not_implemented",
        "reason": "EB-POC-001 iteration 2 — see docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md",
    }

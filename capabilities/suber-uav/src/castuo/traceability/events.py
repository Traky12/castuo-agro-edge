"""Eventos de trazabilidad."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from castuo.common.origen import Origen

ASSET_INGESTED = "asset.ingested"
DETECTION_CREATED = "detection.created"
ASSET_PROPOSED = "asset.proposed"
SEAL_CREATED = "seal.created"
REVIEW_RECORDED = "review.recorded"
PACKAGE_EXPORTED = "package.exported"


@dataclass(frozen=True)
class TraceEvent:
    trace_id: uuid.UUID
    device_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    event_type: str
    actor: uuid.UUID
    sequence_no: int
    occurred_at: datetime
    payload_hash: bytes
    event_hash: bytes
    previous_trace_hash: bytes | None
    schema_version: int
    origen: Origen

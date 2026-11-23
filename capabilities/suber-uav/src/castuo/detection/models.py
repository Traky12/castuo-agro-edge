"""Entidades de detección. Sin `review_status`: la revisión es su propia entidad (C-2)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from castuo.common.origen import Origen


@dataclass(frozen=True)
class Detection:
    detection_id: uuid.UUID
    asset_id: uuid.UUID | None       # nulo cuando la detección aún no propone activo (C-1)
    evidence_id: str
    model_id: str
    model_version: str
    label: str
    confidence: Decimal
    geometry: str | None
    params: dict
    input_hash: bytes
    result_hash: bytes
    detected_at: datetime
    schema_version: int
    origen: Origen

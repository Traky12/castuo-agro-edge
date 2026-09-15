"""Evidence Bridge domain models — provenance-tagged telemetry events, deviations, and reviews.

EB-POC-001 — EXPERIMENTAL. See docs/evidence-bridge/SCOPE_AND_EXCLUSIONS.md.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Provenance(str, enum.Enum):
    """Tags the origin of a field so the bridge never implies certainty the source never gave."""

    PROVIDED = "PROVIDED"
    GENERATED_BY_BRIDGE = "GENERATED_BY_BRIDGE"
    DERIVED = "DERIVED"
    UNKNOWN = "UNKNOWN"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class TelemetryEvent(BaseModel):
    event_id: str
    event_type: str = "TELEMETRY_READING"
    source_system: str
    source_event_id: str
    operation_scope_id: str
    device_id: Optional[str] = None
    device_id_status: Provenance = Provenance.UNKNOWN
    metric: str
    value: float
    unit: str
    occurred_at: datetime
    occurred_at_status: Provenance = Provenance.PROVIDED
    received_at: Optional[datetime] = None
    received_at_status: Provenance = Provenance.GENERATED_BY_BRIDGE
    sequence_number: Optional[int] = None
    sequence_status: Provenance = Provenance.UNKNOWN
    source_config_version: Optional[str] = None
    ingestion_mode: str = "READ_ONLY"
    payload_hash: Optional[str] = None
    previous_event_hash: Optional[str] = None
    schema_version: str = "1.0.0"
    qms_reference: Optional[str] = None
    qms_reference_status: Provenance = Provenance.NOT_AVAILABLE
    review_status: str = "PENDING"


class Deviation(BaseModel):
    deviation_id: str
    operation_scope_id: str
    triggering_event_id: str
    opened_at: datetime
    description: str
    status: str = "OPEN"
    qms_reference: Optional[str] = None
    qms_reference_status: Provenance = Provenance.NOT_AVAILABLE


class ReviewAction(BaseModel):
    action_id: str
    deviation_id: str
    actor_id: str
    actor_id_status: Provenance = Provenance.PROVIDED
    action_type: str
    description: str
    recorded_at: datetime


class EvidenceManifestEntry(BaseModel):
    event_id: str
    payload_hash: str
    previous_event_hash: Optional[str] = None


class EvidenceManifest(BaseModel):
    manifest_id: str
    operation_scope_id: str
    generated_at: datetime
    entries: list[EvidenceManifestEntry]
    manifest_hash: str

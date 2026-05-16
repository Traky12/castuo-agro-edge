from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryReading(BaseModel):
    device_id: str
    readings: dict[str, float] = Field(default_factory=dict)
    unit: str | None = None


@router.post("/ingest")
def ingest(reading: TelemetryReading):
    """Accept telemetry for local buffering (v0.1 stub)."""
    return {
        "accepted": True,
        "device_id": reading.device_id,
        "buffered": True,
        "note": "Wire to gateway.buffering in v0.1",
    }

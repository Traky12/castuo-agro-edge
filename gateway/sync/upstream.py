"""Sync buffered telemetry to CASTÚO-SYSTEM core when online."""

from gateway.config import settings


async def flush_pending() -> dict:
    if not settings.castuo_api_url:
        return {"flushed": 0, "reason": "CASTUO_API_URL not configured"}
    return {"flushed": 0, "reason": "v0.1 stub — implement batch upload"}

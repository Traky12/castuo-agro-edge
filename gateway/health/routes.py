from datetime import datetime, timezone

from fastapi import APIRouter

from gateway.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "castuo-agro-edge",
        "site_id": settings.site_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "offline_capable": True,
    }

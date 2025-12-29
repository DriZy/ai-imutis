"""Health and readiness endpoints."""
from datetime import datetime

from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", summary="Service healthcheck")
async def healthcheck() -> dict:
    """Return simple health status."""

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ai-imutis-backend",
    }

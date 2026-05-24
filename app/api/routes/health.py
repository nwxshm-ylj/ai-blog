from __future__ import annotations

from fastapi import APIRouter

from app.schemas.health import HealthCheck

router = APIRouter(prefix="/health")


@router.get("", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    return HealthCheck(status="ok")


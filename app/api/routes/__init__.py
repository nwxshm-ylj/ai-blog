from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.blog import router as blog_router
from app.api.routes.health import router as health_router
from app.api.routes.home import router as home_router

api_router = APIRouter()
api_router.include_router(home_router)
api_router.include_router(blog_router)
api_router.include_router(health_router, tags=["health"])

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.blog import router as blog_router
from app.api.routes.health import router as health_router
from app.api.routes.lab import router as lab_router
from app.api.routes.home import router as home_router
from app.api.routes.projects import router as projects_router
from app.api.routes.seo import router as seo_router

api_router = APIRouter()
api_router.include_router(home_router)
api_router.include_router(blog_router)
api_router.include_router(projects_router)
api_router.include_router(lab_router)
api_router.include_router(seo_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(health_router, tags=["health"])


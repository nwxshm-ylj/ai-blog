from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.middleware.request_id import RequestIdMiddleware


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie=settings.session_cookie_name,
        https_only=settings.app_env not in {"local", "development", "test"},
        same_site="lax",
    )
    app.add_middleware(RequestIdMiddleware)

from __future__ import annotations

import secrets

from fastapi import HTTPException, Request, status

CSRF_SESSION_KEY = "csrf_token"


def csrf_token(request: Request) -> str:
    token = request.session.get(CSRF_SESSION_KEY)
    if not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        request.session[CSRF_SESSION_KEY] = token
    return token


def verify_csrf_token(request: Request, token: str | None) -> None:
    expected = request.session.get(CSRF_SESSION_KEY)
    if not isinstance(expected, str) or not token or not secrets.compare_digest(expected, token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="表单令牌无效。",
        )

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated
from urllib.parse import quote

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.models.user import User
from app.services.auth import SESSION_USER_ID_KEY, get_user_by_session_id


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def require_admin_user(request: Request, session: SessionDependency) -> User:
    user = await get_user_by_session_id(
        session,
        request.session.get(SESSION_USER_ID_KEY),
    )
    if user is None:
        next_url = quote(str(request.url.path), safe="/")
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": f"/auth/login?next={next_url}"},
        )
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access is required.",
        )

    return user

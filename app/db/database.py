from __future__ import annotations

from collections.abc import AsyncGenerator
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _engine_connect_args() -> dict[str, bool]:
    host = urlparse(settings.database_url).hostname
    if host in {"localhost", "127.0.0.1", "::1"}:
        return {"ssl": False}
    return {}


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=_engine_connect_args(),
)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

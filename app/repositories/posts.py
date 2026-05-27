from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Post)

    async def list_admin(self) -> Sequence[Post]:
        statement = select(Post).order_by(Post.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def list_public(self, *, offset: int = 0, limit: int = 10) -> Sequence[Post]:
        statement = (
            select(Post)
            .options(selectinload(Post.category), selectinload(Post.tags), selectinload(Post.author))
            .where(Post.is_published.is_(True))
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_slug(self, slug: str) -> Post | None:
        return await self.get_by(slug=slug)

    async def get_public_by_slug(self, slug: str) -> Post | None:
        statement = (
            select(Post)
            .options(selectinload(Post.category), selectinload(Post.tags), selectinload(Post.author))
            .where(Post.slug == slug, Post.is_published.is_(True))
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

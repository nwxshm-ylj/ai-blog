from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Post)

    async def list_admin(self) -> Sequence[Post]:
        statement = select(Post).order_by(Post.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_slug(self, slug: str) -> Post | None:
        return await self.get_by(slug=slug)

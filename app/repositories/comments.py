from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.post import Post
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Comment)

    async def list_admin(self) -> Sequence[Comment]:
        statement = (
            select(Comment)
            .options(selectinload(Comment.user), selectinload(Comment.post))
            .order_by(Comment.created_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def list_approved_by_post_slug(self, slug: str) -> Sequence[Comment]:
        statement = (
            select(Comment)
            .join(Post, Comment.post_id == Post.id)
            .options(selectinload(Comment.user))
            .where(Post.slug == slug, Comment.is_approved.is_(True))
            .order_by(Comment.created_at.asc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_with_context(self, comment_id: uuid.UUID) -> Comment | None:
        statement = (
            select(Comment)
            .options(selectinload(Comment.user), selectinload(Comment.post))
            .where(Comment.id == comment_id)
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

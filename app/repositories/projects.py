from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Project)

    async def list_admin(self) -> Sequence[Project]:
        statement = select(Project).order_by(Project.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def list_public(self, *, offset: int = 0, limit: int = 12) -> Sequence[Project]:
        statement = select(Project).order_by(Project.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def list_featured(self, *, limit: int = 4) -> Sequence[Project]:
        statement = (
            select(Project)
            .where(Project.featured.is_(True))
            .order_by(Project.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_slug(self, slug: str) -> Project | None:
        return await self.get_by(slug=slug)

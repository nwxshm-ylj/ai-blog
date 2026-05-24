from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email_or_username(self, identifier: str) -> User | None:
        statement = (
            select(User)
            .where((User.email == identifier) | (User.username == identifier))
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

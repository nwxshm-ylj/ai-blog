from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email_or_username(self, identifier: str) -> User | None:
        normalized_identifier = identifier.lower()
        statement = (
            select(User)
            .where(
                (func.lower(User.email) == normalized_identifier)
                | (func.lower(User.username) == normalized_identifier)
            )
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == email.lower()).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(func.lower(User.username) == username.lower()).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

from __future__ import annotations

import uuid
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def get(self, model_id: uuid.UUID) -> Optional[ModelType]:
        return await self.session.get(self.model, model_id)

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        statement: Select[tuple[ModelType]] = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def get_by(self, **filters: Any) -> Optional[ModelType]:
        statement = select(self.model).filter_by(**filters).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

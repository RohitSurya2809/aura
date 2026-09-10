from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from sqlalchemy import select

from aura.infrastructure.database.base import Base

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT", bound=Base)


class SQLAlchemyRepository(Generic[ModelT]):
    """Base repository providing common CRUD operations."""

    model_class: ClassVar[type[Base]]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        return await self._session.get(self.model_class, entity_id)  # type: ignore[arg-type]

    async def create(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        merged: ModelT = await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(merged)
        return merged

    async def delete(self, entity_id: UUID) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True

    async def list_all(self) -> list[ModelT]:
        result = await self._session.execute(select(self.model_class))
        return list(result.scalars().all())  # type: ignore[arg-type]

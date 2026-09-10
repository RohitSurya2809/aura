from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from sqlalchemy import func, select

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


from aura.infrastructure.database.models import Conversation, Message  # noqa: E402


class ConversationRepository(SQLAlchemyRepository[Conversation]):
    """Repository for Conversation entities."""

    model_class = Conversation

    async def list_all(self) -> list[Conversation]:
        """List all conversations (most recent first)."""
        result = await self._session.execute(
            select(Conversation).order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())


class MessageRepository(SQLAlchemyRepository[Message]):
    """Repository for Message entities."""

    model_class = Message

    async def get_by_conversation(self, conversation_id: UUID) -> list[Message]:
        """Get all messages for a conversation, ordered by sequence."""
        result = await self._session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence.asc())
        )
        return list(result.scalars().all())

    async def get_last_n(self, conversation_id: UUID, n: int) -> list[Message]:
        """Get last N messages from a conversation."""
        messages = await self.get_by_conversation(conversation_id)
        return messages[-n:] if n > 0 else []

    async def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
    ) -> Message:
        """Add a new message to a conversation."""
        # Get the next sequence number
        result = await self._session.execute(
            select(func.max(Message.sequence)).where(Message.conversation_id == conversation_id)
        )
        max_seq = result.scalar() or 0

        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence=max_seq + 1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        return await self.create(message)

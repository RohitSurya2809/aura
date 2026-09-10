from __future__ import annotations

from uuid import UUID  # noqa: TC003

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aura.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SystemMeta(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """System metadata key-value store for tracking schema version, initialization state, etc."""

    __tablename__ = "system_meta"

    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(2048), nullable=False)


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A persistent conversation thread."""

    __tablename__ = "conversation"

    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Message(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single message in a conversation."""

    __tablename__ = "message"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sequence: Mapped[int] = mapped_column(nullable=False, index=True)

    conversation: Mapped[Conversation] = relationship(
        "Conversation",
        back_populates="messages",
    )

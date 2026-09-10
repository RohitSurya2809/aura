from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from aura.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SystemMeta(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """System metadata key-value store for tracking schema version, initialization state, etc."""

    __tablename__ = "system_meta"

    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(2048), nullable=False)

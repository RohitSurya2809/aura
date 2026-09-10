from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import sqlalchemy
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aura.core.errors import DatabaseError
from aura.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from aura.core.config import DatabaseSettings

logger = get_logger(__name__)


class DatabaseEngine:
    """Manages the async SQLAlchemy engine and session factory."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def initialize(self) -> None:
        """Create the engine and session factory."""
        try:
            self._engine = create_async_engine(
                self._settings.async_url,
                echo=self._settings.echo,
                pool_size=self._settings.pool_size,
                max_overflow=self._settings.max_overflow,
            )
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            logger.info(
                "database_engine_initialized",
                host=self._settings.host,
                port=self._settings.port,
            )
        except Exception as exc:
            raise DatabaseError(f"Failed to initialize database engine: {exc}") from exc

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise DatabaseError("Database engine not initialized. Call initialize() first.")
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional async session scope."""
        if self._session_factory is None:
            raise DatabaseError("Database engine not initialized. Call initialize() first.")
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def dispose(self) -> None:
        """Dispose the engine and release connections."""
        if self._engine is not None:
            await self._engine.dispose()
            logger.info("database_engine_disposed")
            self._engine = None
            self._session_factory = None

    async def check_connection(self) -> bool:
        """Verify database connectivity."""
        try:
            async with self.engine.connect() as conn:
                await conn.execute(sqlalchemy.text("SELECT 1"))
            return True
        except Exception as exc:
            logger.error("database_connection_check_failed", error=str(exc))
            return False

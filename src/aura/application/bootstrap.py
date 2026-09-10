from __future__ import annotations

from aura.core.config import AuraSettings, get_settings
from aura.core.errors import ConfigurationError
from aura.core.logging import get_logger, setup_logging
from aura.infrastructure.database.engine import DatabaseEngine

logger = get_logger(__name__)


class AuraApplication:
    """Application root that owns and manages all subsystem lifecycles."""

    def __init__(self, settings: AuraSettings) -> None:
        self._settings = settings
        self._db: DatabaseEngine | None = None
        self._started = False

    @property
    def settings(self) -> AuraSettings:
        return self._settings

    @property
    def db(self) -> DatabaseEngine:
        if self._db is None:
            raise ConfigurationError("Database not initialized. Call startup() first.")
        return self._db

    @property
    def is_started(self) -> bool:
        return self._started

    async def startup(self) -> None:
        """Initialize all application subsystems."""
        if self._started:
            return

        setup_logging(self._settings.logging)
        logger.info(
            "aura_starting",
            app_name=self._settings.app_name,
            version=self._settings.version,
            environment=self._settings.environment,
        )

        self._db = DatabaseEngine(self._settings.database)
        await self._db.initialize()

        self._started = True
        logger.info("aura_started")

    async def shutdown(self) -> None:
        """Shut down all application subsystems gracefully."""
        if not self._started:
            return

        logger.info("aura_shutting_down")

        if self._db is not None:
            await self._db.dispose()
            self._db = None

        self._started = False
        logger.info("aura_stopped")

    async def health_check(self) -> dict[str, object]:
        """Check health of all subsystems."""
        db_ok = False
        if self._db is not None:
            db_ok = await self._db.check_connection()

        return {
            "status": "healthy" if db_ok else "degraded",
            "version": self._settings.version,
            "environment": self._settings.environment,
            "database": "connected" if db_ok else "disconnected",
        }


def create_application(settings: AuraSettings | None = None) -> AuraApplication:
    """Factory function to create a configured AuraApplication instance."""
    if settings is None:
        try:
            settings = get_settings()
        except Exception as exc:
            raise ConfigurationError(f"Failed to load configuration: {exc}") from exc
    return AuraApplication(settings)

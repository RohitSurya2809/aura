from __future__ import annotations

import pytest

from aura.core.config import DatabaseSettings
from aura.infrastructure.database.engine import DatabaseEngine


@pytest.fixture
def integration_db_settings() -> DatabaseSettings:
    """Database settings for integration tests. Uses a separate test database."""
    return DatabaseSettings(
        host="localhost",
        port=5432,
        user="aura_test",
        password="aura_test",  # type: ignore[arg-type]
        name="aura_test",
    )


@pytest.fixture
async def db_engine(integration_db_settings: DatabaseSettings) -> DatabaseEngine:
    """Provide an initialized DatabaseEngine for integration tests."""
    engine = DatabaseEngine(integration_db_settings)
    await engine.initialize()
    yield engine  # type: ignore[misc]
    await engine.dispose()

from __future__ import annotations

import pytest

from aura.core.config import AuraSettings, DatabaseSettings, LoggingSettings


@pytest.fixture
def db_settings() -> DatabaseSettings:
    """Test database settings pointing to a test database."""
    return DatabaseSettings(
        host="localhost",
        port=5432,
        user="aura_test",
        password="aura_test",  # type: ignore[arg-type]
        name="aura_test",
    )


@pytest.fixture
def log_settings() -> LoggingSettings:
    return LoggingSettings(level="DEBUG", format="console")


@pytest.fixture
def settings(db_settings: DatabaseSettings, log_settings: LoggingSettings) -> AuraSettings:
    """Complete test settings."""
    return AuraSettings(
        environment="testing",
        debug=True,
        database=db_settings,
        logging=log_settings,
    )

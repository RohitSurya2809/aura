from __future__ import annotations

import pytest  # noqa: TC002
from pydantic import SecretStr

from aura.core.config import (
    AuraSettings,
    DatabaseSettings,
    GeminiSettings,
    LoggingSettings,
    OpenRouterSettings,
)


class TestDatabaseSettings:
    def test_defaults(self) -> None:
        settings = DatabaseSettings()
        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.user == "aura"
        assert settings.name == "aura"
        assert settings.echo is False
        assert settings.pool_size == 5

    def test_async_url(self) -> None:
        settings = DatabaseSettings()
        url = settings.async_url
        assert url.startswith("postgresql+asyncpg://")
        assert "localhost" in url
        assert "5432" in url

    def test_sync_url(self) -> None:
        settings = DatabaseSettings()
        url = settings.sync_url
        assert url.startswith("postgresql+psycopg2://")

    def test_custom_values(self) -> None:
        settings = DatabaseSettings(
            host="db.example.com",
            port=5433,
            user="custom",
            password=SecretStr("secret"),
            name="mydb",
        )
        assert "db.example.com" in settings.async_url
        assert "5433" in settings.async_url
        assert "custom" in settings.async_url
        assert "mydb" in settings.async_url

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AURA_DB_HOST", "remotehost")
        monkeypatch.setenv("AURA_DB_PORT", "9999")
        settings = DatabaseSettings()
        assert settings.host == "remotehost"
        assert settings.port == 9999


class TestLoggingSettings:
    def test_defaults(self) -> None:
        settings = LoggingSettings()
        assert settings.level == "INFO"
        assert settings.format == "console"

    def test_effective_level(self) -> None:
        import logging

        settings = LoggingSettings(level="DEBUG")
        assert settings.effective_level == logging.DEBUG

    def test_json_format(self) -> None:
        settings = LoggingSettings(format="json")
        assert settings.format == "json"


class TestGeminiSettings:
    def test_not_configured_by_default(self) -> None:
        settings = GeminiSettings()
        assert settings.is_configured is False
        assert settings.api_key is None

    def test_configured_with_key(self) -> None:
        settings = GeminiSettings(api_key=SecretStr("test-key"))
        assert settings.is_configured is True


class TestOpenRouterSettings:
    def test_not_configured_by_default(self) -> None:
        settings = OpenRouterSettings()
        assert settings.is_configured is False

    def test_configured_with_key(self) -> None:
        settings = OpenRouterSettings(api_key=SecretStr("test-key"))
        assert settings.is_configured is True


class TestAuraSettings:
    def test_defaults(self) -> None:
        settings = AuraSettings()
        assert settings.app_name == "aura"
        assert settings.environment == "development"
        assert settings.debug is False
        assert isinstance(settings.database, DatabaseSettings)
        assert isinstance(settings.logging, LoggingSettings)

    def test_testing_environment(self) -> None:
        settings = AuraSettings(environment="testing", debug=True)
        assert settings.environment == "testing"
        assert settings.debug is True

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL connection settings."""

    model_config = SettingsConfigDict(env_prefix="AURA_DB_")

    host: str = "localhost"
    port: int = 5432
    user: str = "aura"
    password: SecretStr = SecretStr("aura")
    name: str = "aura"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    @property
    def async_url(self) -> str:
        p = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{p}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        p = self.password.get_secret_value()
        return f"postgresql+psycopg2://{self.user}:{p}@{self.host}:{self.port}/{self.name}"


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(env_prefix="AURA_LOG_")

    level: str = "INFO"
    format: Literal["json", "console"] = "console"

    @property
    def effective_level(self) -> int:
        level: int = getattr(logging, self.level.upper(), logging.INFO)
        return level


class GeminiSettings(BaseSettings):
    """Google Gemini provider settings."""

    model_config = SettingsConfigDict(env_prefix="AURA_GEMINI_")

    api_key: SecretStr | None = None
    model: str = "gemini-2.0-flash"

    @property
    def is_configured(self) -> bool:
        return self.api_key is not None


class OpenRouterSettings(BaseSettings):
    """OpenRouter provider settings."""

    model_config = SettingsConfigDict(env_prefix="AURA_OPENROUTER_")

    api_key: SecretStr | None = None
    model: str = "anthropic/claude-sonnet-4"

    @property
    def is_configured(self) -> bool:
        return self.api_key is not None


class AuraSettings(BaseSettings):
    """Root application settings."""

    model_config = SettingsConfigDict(
        env_prefix="AURA_",
        env_nested_delimiter="__",
        env_file=str(Path.cwd() / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "aura"
    version: str = "0.1.0"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False

    database: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()
    gemini: GeminiSettings = GeminiSettings()
    openrouter: OpenRouterSettings = OpenRouterSettings()


def get_settings() -> AuraSettings:
    """Load settings from environment and .env file."""
    return AuraSettings()

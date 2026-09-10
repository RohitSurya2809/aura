# Changelog

All notable changes to Aura will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-09-10

### Added

- Project structure with clean architecture layers (core, infrastructure, application, interfaces)
- Configuration system using pydantic-settings with environment variable support
- Structured logging via structlog with JSON and console output modes
- Application error hierarchy (AuraError, ConfigurationError, DatabaseError, etc.)
- Async PostgreSQL integration with SQLAlchemy 2.x and asyncpg
- Database engine with connection pooling and session management
- SQLAlchemy declarative base with UUID primary key and timestamp mixins
- Alembic migration infrastructure
- Repository pattern for data access
- Application bootstrap with lifecycle management
- Minimal CLI with `aura --version` and `aura status` commands
- Unit and integration test infrastructure with pytest
- Code quality tooling: Ruff, Black, mypy
- LLM provider protocol (Gemini and OpenRouter abstractions, implementation pending)

# Aura

A lightweight, agentic personal AI companion designed to understand its user, remember context, reason about tasks, use tools, and progressively act on the user's behalf.

> **Status**: Phase 1 — Foundation (in progress)

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for package management
- PostgreSQL 15+ (local instance)

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd aura

# Install dependencies
uv sync --all-extras

# Copy environment template and configure
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Run database migrations
uv run alembic upgrade head

# Verify installation
uv run aura --version
uv run aura status
```

## Configuration

Aura uses environment variables for configuration. Copy `.env.example` to `.env` and adjust:

| Variable | Default | Description |
|---|---|---|
| `AURA_ENVIRONMENT` | `development` | Environment: development, testing, production |
| `AURA_DEBUG` | `false` | Enable debug mode |
| `AURA_DB_HOST` | `localhost` | PostgreSQL host |
| `AURA_DB_PORT` | `5432` | PostgreSQL port |
| `AURA_DB_USER` | `aura` | PostgreSQL user |
| `AURA_DB_PASSWORD` | `aura` | PostgreSQL password |
| `AURA_DB_NAME` | `aura` | PostgreSQL database name |
| `AURA_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `AURA_LOG_FORMAT` | `console` | Log format: console or json |

LLM provider keys (optional, for future phases):

| Variable | Description |
|---|---|
| `AURA_GEMINI_API_KEY` | Google Gemini API key |
| `AURA_OPENROUTER_API_KEY` | OpenRouter API key |

## Development

```bash
# Run tests (unit only)
uv run pytest tests/unit/ -v

# Run all tests (requires PostgreSQL)
uv run pytest -v

# Run integration tests only
uv run pytest tests/integration/ -v -m integration

# Lint
uv run ruff check src/ tests/

# Format
uv run black src/ tests/

# Type check
uv run mypy

# Format check (no changes)
uv run black --check src/ tests/
```

## Project Structure

```
src/aura/
├── core/               # Domain layer: config, errors, logging, protocols
├── infrastructure/     # Infrastructure: database, providers
│   ├── database/       # SQLAlchemy engine, models, repositories
│   └── providers/      # LLM provider implementations (future)
├── application/        # Application layer: bootstrap, services
└── interfaces/
    └── cli/            # Typer CLI interface
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## Cross-Platform

Aura is designed for both Windows and Linux. No OS-specific logic exists in core modules. Platform-specific capabilities will be isolated behind adapters in future phases.

## License

MIT

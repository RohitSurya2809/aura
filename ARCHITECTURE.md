# Aura Architecture

## Overview

Aura is a lightweight, agentic personal AI companion. It is designed as a modular, layered application that can support multiple interfaces (CLI, desktop, web, voice) on top of a shared core.

The architecture follows **Clean Architecture** principles with strict dependency direction: outer layers depend on inner layers, never the reverse. Infrastructure implements abstractions defined in the core via dependency inversion.

```
Interfaces (CLI, future Desktop/Web/Voice)
    │
    ▼
Application (bootstrap, services, use cases)
    │
    ▼
Domain / Core (config, errors, logging, protocols)
    │
    ▼
Infrastructure (database, LLM providers)
```

> **Note**: Infrastructure sits at the bottom of the diagram but is an *outer* layer in Clean Architecture terms. It implements protocols defined in Core, and is injected into the Application layer — Core never imports from Infrastructure directly.

## Package Structure

```
src/aura/
├── __init__.py              # Package version
├── __main__.py              # `python -m aura` entry point
├── core/                    # Domain layer
│   ├── config.py            # Typed settings via pydantic-settings
│   ├── errors.py            # Application error hierarchy
│   ├── logging.py           # Structured logging setup (structlog)
│   └── protocols.py         # Abstract interfaces (LLM provider, repositories)
├── infrastructure/          # Infrastructure layer
│   ├── database/
│   │   ├── engine.py        # Async SQLAlchemy engine and session factory
│   │   ├── base.py          # Declarative base, mixins (UUID PK, timestamps)
│   │   ├── models.py        # ORM models
│   │   └── repositories.py  # Repository implementations
│   └── providers/           # LLM provider implementations (future)
├── application/             # Application layer
│   ├── bootstrap.py         # Composition root, lifecycle management
│   └── services/            # Application services (future)
└── interfaces/              # Interface layer
    └── cli/
        └── app.py           # Typer CLI
```

### Core (`src/aura/core/`)

The innermost layer. Contains configuration, error definitions, logging setup, and protocol (interface) definitions. Has no dependencies on infrastructure or application code.

- **`config.py`** — Strongly typed settings using `pydantic-settings`. All configuration flows from environment variables. Secrets are never hardcoded.
- **`errors.py`** — Hierarchical exception classes that distinguish configuration, database, infrastructure, application, and validation errors.
- **`logging.py`** — Structured logging configuration using `structlog`. Supports console (development) and JSON (production) output formats.
- **`protocols.py`** — Abstract base classes and `Protocol` definitions for LLM providers, repositories, and other contracts that infrastructure must implement.

### Infrastructure (`src/aura/infrastructure/`)

Implements the technical concerns defined by Core protocols.

- **`database/`** — Async PostgreSQL integration via SQLAlchemy 2.x and asyncpg. Provides engine creation, session management, the declarative ORM base with standard mixins, concrete models, and repository implementations.
- **`providers/`** — LLM provider implementations. Currently contains only protocol stubs. Gemini and OpenRouter implementations will be added in Phase 2.

### Application (`src/aura/application/`)

Orchestrates the system. Responsible for composing dependencies and managing the application lifecycle.

- **`bootstrap.py`** — The composition root. Creates configuration, initializes infrastructure (database, logging), wires repositories and services, and exposes the assembled application context. Manages startup and shutdown.
- **`services/`** — Application services that implement use cases. Currently empty; will contain conversation, memory, and agent services in future phases.

### Interfaces (`src/aura/interfaces/`)

Thin adapters that expose Aura's capabilities to users.

- **`cli/app.py`** — Typer-based CLI. Contains no business logic. Delegates to the application layer for all operations.

## Dependency Rules

1. **Core** depends on nothing within Aura (only stdlib and Pydantic).
2. **Infrastructure** depends on Core (imports protocols and config).
3. **Application** depends on Core and receives Infrastructure implementations via injection.
4. **Interfaces** depend on Application (calls bootstrap, invokes services).

```
interfaces/ → application/ → core/ ← infrastructure/
```

Infrastructure and Interfaces never import each other. Application receives infrastructure implementations through the bootstrap/composition root, not through direct imports.

## Configuration

All configuration is environment-driven using `pydantic-settings`. Variables are grouped by prefix:

| Prefix | Scope |
|---|---|
| `AURA_` | General application settings (environment, debug) |
| `AURA_DB_` | PostgreSQL connection (host, port, user, password, name) |
| `AURA_LOG_` | Logging (level, format) |
| `AURA_GEMINI_` | Gemini provider settings (future) |
| `AURA_OPENROUTER_` | OpenRouter provider settings (future) |

A `.env.example` file documents all supported variables with safe defaults. The `.env` file is gitignored.

## Database

- **Engine**: Async SQLAlchemy 2.x with the `asyncpg` dialect.
- **Session management**: Centralized async session factory. Sessions are not created ad-hoc throughout the codebase.
- **ORM base**: Declarative base with standard mixins for UUID primary keys and created/updated timestamps.
- **Migrations**: Alembic with async support. Migration scripts live in `alembic/versions/`.
- **Data access**: Repository pattern. Repositories encapsulate all database queries and are defined as protocols in Core, implemented in Infrastructure.

### Future schema

The database architecture is designed to support these entities in later phases:

- User, Conversation, Message
- Memory (with future pgvector embeddings)
- Task, AgentRun, ToolExecution
- Skill

These are **not implemented** in Phase 1. The ORM base and migration infrastructure are ready to support them.

## Error Handling

```
AuraError
├── ConfigurationError
├── DatabaseError
├── InfrastructureError
├── ApplicationError
└── ValidationError
```

All Aura exceptions inherit from `AuraError`. This allows callers to catch broad or specific error categories. Sensitive details (credentials, internal paths) are never included in error messages exposed to users.

## Logging

Structured logging via `structlog`.

- **Development**: Console renderer with colors and human-readable output.
- **Production / CI**: JSON renderer for machine parsing.
- Configured via `AURA_LOG_LEVEL` and `AURA_LOG_FORMAT`.
- Secrets are never logged. The logging pipeline filters or avoids sensitive fields.

## LLM Strategy

Aura supports two LLM provider families:

1. **Google Gemini**
2. **OpenRouter**

No other providers (Ollama, vLLM, Bedrock, etc.) are in scope.

Providers implement a common protocol defined in `core/protocols.py`. The application layer depends only on the protocol, never on a specific provider. Provider selection and initialization happen in the bootstrap layer.

> **Phase 1 status**: Protocol defined. Concrete implementations are deferred to Phase 2.

## Cross-Platform

Aura targets both Windows and Linux. Design rules:

- No OS-specific logic in `core/`, `application/`, or `infrastructure/database/`.
- Path handling uses `pathlib` exclusively.
- Future OS-specific capabilities (shell, filesystem, desktop automation) will be isolated behind platform adapters.

## Future Architecture

The current foundation is designed to support the following without structural rewrites:

```
Aura CLI ─┐
Aura Desktop ─┤
Aura Voice ─┤
Aura Web ─────┤
              ▼
     Application / Agent Core
              │
              ├── Memory (PostgreSQL + pgvector)
              ├── Conversation
              ├── LLM Providers (Gemini, OpenRouter)
              ├── Tools (file, shell, web, git)
              └── Skills / MCP
```

Each future capability maps to a bounded area of the codebase:

| Capability | Location | Phase |
|---|---|---|
| LLM integration | `infrastructure/providers/` | 2 |
| Conversation engine | `application/services/` + `infrastructure/database/models.py` | 2 |
| Memory | `application/services/` + new models + pgvector | 3 |
| Agent loop | `application/services/` | 4 |
| Tools | `infrastructure/tools/` (new) | 5 |
| Skills / MCP | `infrastructure/extensions/` (new) | 6 |
| Additional interfaces | `interfaces/` (new subpackages) | 7 |

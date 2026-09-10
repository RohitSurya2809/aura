# Aura Roadmap

## Phase 1 — Foundation *(In Progress)*

Establish the production-quality application foundation. Project structure with clean architecture layers, strongly typed configuration, structured logging, error hierarchy, async PostgreSQL integration with SQLAlchemy 2.x, Alembic migrations, repository pattern, application bootstrap, minimal CLI shell, and testing/quality infrastructure.

## Phase 2 — Core Intelligence *(Planned)*

Integrate LLM providers (Gemini and OpenRouter) behind the provider abstraction. Build the conversation engine with message persistence, session management, and a basic interactive chat loop through the CLI.

## Phase 3 — Memory *(Planned)*

Implement persistent memory with context management. Add pgvector to PostgreSQL for semantic search over stored memories. Enable Aura to recall prior conversations, user preferences, and project context across sessions.

## Phase 4 — Agency *(Planned)*

Build the agent loop with planning and reasoning capabilities. Implement the tool execution framework that allows Aura to decide when and how to use tools, chain actions, and recover from failures.

## Phase 5 — Capabilities *(Planned)*

Add concrete tool implementations: file operations, shell command execution, web search/fetching, and git operations. Each tool is isolated behind a standard interface and registered with the agent framework.

## Phase 6 — Extensions *(Planned)*

Introduce the skills system for reusable, composable behaviors. Add MCP (Model Context Protocol) integration for external tool servers. Establish a plugin architecture for community and user extensions.

## Phase 7 — Interfaces *(Planned)*

Expand beyond the CLI. Add a desktop application, voice interface, and web interface. All interfaces share the same application core — no business logic is duplicated across interfaces.

## Phase 8 — Autonomy *(Planned)*

Enable proactive behavior: background monitoring, scheduled operations, and autonomous task execution. Aura can act on the user's behalf without being explicitly prompted, within configured boundaries.

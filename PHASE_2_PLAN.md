# Phase 2 Implementation Plan

## Parallel Work Items

### Fork 1: LLM Domain & Contracts (2A)
- `src/aura/core/llm_contracts.py` — Message, Role, ProviderResponse, Usage models
- `src/aura/core/llm_provider.py` — LLMProvider protocol
- `src/aura/core/llm_config.py` — Provider configuration schemas

### Fork 2: Providers (2B + 2C)
- `src/aura/infrastructure/providers/base.py` — Base provider implementation
- `src/aura/infrastructure/providers/gemini.py` — Gemini implementation
- `src/aura/infrastructure/providers/openrouter.py` — OpenRouter implementation

### Fork 3: Provider Router (2D)
- `src/aura/infrastructure/providers/router.py` — Provider router with fallback logic
- `src/aura/application/services/llm_service.py` — LLM service (high-level wrapper)

### Fork 4: Conversation Models & DB (2E + 2F + 2G)
- `src/aura/infrastructure/database/models.py` — Add Conversation, Message models
- Alembic migration for new models
- `src/aura/infrastructure/database/repositories.py` — Add ConversationRepository, MessageRepository

### Fork 5: Conversation Engine (2H)
- `src/aura/application/services/conversation_service.py` — Orchestrate conversations
- `src/aura/domain/context_builder.py` — Build context from history

### Fork 6: CLI & Integration (2I + 2J)
- Extend `src/aura/interfaces/cli/app.py` — Add conversation commands
- Support new conversation, resume conversation, list conversations

### Fork 7: Tests
- Unit tests for LLM contracts
- Tests for Gemini/OpenRouter (mocked)
- Router tests
- Conversation service tests
- CLI command tests

### Fork 8: Documentation & Quality
- Update README.md
- Update ARCHITECTURE.md
- Create PHASE_2_COMPLETION.md template
- Run quality checks

## Dependencies

- Fork 1 (LLM contracts) → needed by Fork 2, 3, 5
- Fork 2 (Providers) → needed by Fork 3
- Fork 3 (Router) → needed by Fork 5
- Fork 4 (DB) → needed by Fork 5
- Fork 5 (Engine) → needed by Fork 6
- All → Fork 7 (Tests)
- All → Fork 8 (Documentation)

## Sequential Steps

1. **Fork 1** creates LLM contracts (no dependencies)
2. **Fork 2** implements providers (depends on Fork 1)
3. **Fork 3** creates router (depends on Fork 1, 2)
4. **Fork 4** creates DB models (independent)
5. **Fork 5** creates engine (depends on 1, 3, 4)
6. **Fork 6** extends CLI (depends on 5)
7. **Forks 7 & 8** in parallel after main work done

## Key Design Decisions

- Message models use enums for Role
- Provider interface is simple (generate method)
- Router supports priority and fallback
- Conversation context is built incrementally
- Streaming is optional (implement if clean)
- No memory extraction in Phase 2
- No agent loop in Phase 2

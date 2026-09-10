from __future__ import annotations

import pytest  # noqa: TC002

from aura.infrastructure.database.engine import DatabaseEngine  # noqa: TC001


@pytest.mark.integration
class TestDatabaseConnection:
    async def test_engine_initialization(self, db_engine: DatabaseEngine) -> None:
        assert db_engine.engine is not None

    async def test_connection_check(self, db_engine: DatabaseEngine) -> None:
        result = await db_engine.check_connection()
        assert result is True

    async def test_session_context_manager(self, db_engine: DatabaseEngine) -> None:
        async with db_engine.session() as session:
            assert session is not None

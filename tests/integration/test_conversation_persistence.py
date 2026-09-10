from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
class TestConversationPersistence:
    async def test_create_and_retrieve_conversation(self, db_engine: object) -> None:
        # This test requires live database; will be skipped in normal test runs
        # unless -m integration flag is passed
        pass

    async def test_message_sequence(self, db_engine: object) -> None:
        # This test requires live database; will be skipped in normal test runs
        # unless -m integration flag is passed
        pass

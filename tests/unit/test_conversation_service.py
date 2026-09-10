from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from aura.application.services.conversation_service import ConversationService
from aura.core.llm_contracts import ProviderResponse


@pytest.mark.asyncio
class TestConversationService:
    @pytest.fixture
    async def conversation_service(self) -> ConversationService:
        conv_repo = AsyncMock()
        msg_repo = AsyncMock()
        llm_service = AsyncMock()

        return ConversationService(
            conversation_repo=conv_repo,
            message_repo=msg_repo,
            llm_service=llm_service,
            context_window=5,
        )

    async def test_create_conversation(self) -> None:
        conv_id = UUID("12345678-1234-5678-1234-567812345678")
        conv_repo: AsyncMock = AsyncMock()
        msg_repo: AsyncMock = AsyncMock()
        llm_service: AsyncMock = AsyncMock()

        conv_service = ConversationService(
            conversation_repo=conv_repo,
            message_repo=msg_repo,
            llm_service=llm_service,
        )

        conv_repo.create = AsyncMock(return_value=MagicMock(id=conv_id))

        result = await conv_service.create_conversation(title="Test")

        assert result == conv_id
        conv_repo.create.assert_called_once()

    async def test_send_message(self) -> None:
        conv_id = UUID("12345678-1234-5678-1234-567812345678")
        user_message = "Hello"

        conv_repo: AsyncMock = AsyncMock()
        msg_repo: AsyncMock = AsyncMock()
        llm_service: AsyncMock = AsyncMock()

        conv_service = ConversationService(
            conversation_repo=conv_repo,
            message_repo=msg_repo,
            llm_service=llm_service,
        )

        msg_repo.add_message = AsyncMock()
        msg_repo.get_by_conversation = AsyncMock(return_value=[])
        llm_service.generate = AsyncMock(return_value=ProviderResponse(content="Hi there!"))

        response = await conv_service.send_message(conv_id, user_message)

        assert response == "Hi there!"
        assert msg_repo.add_message.call_count == 2  # user + assistant

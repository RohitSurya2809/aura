from __future__ import annotations

from typing import TYPE_CHECKING

from aura.core.llm_contracts import LLMRequest, Message, MessageRole
from aura.core.logging import get_logger

if TYPE_CHECKING:
    from uuid import UUID

    from aura.application.services.llm_service import LLMService
    from aura.infrastructure.database.repositories import (
        ConversationRepository,
        MessageRepository,
    )


logger = get_logger(__name__)


class ConversationService:
    """High-level conversation orchestration service."""

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        llm_service: LLMService,
        context_window: int = 10,
    ) -> None:
        self._conversation_repo = conversation_repo
        self._message_repo = message_repo
        self._llm_service = llm_service
        self._context_window = context_window
        logger.info(
            "conversation_service_initialized",
            context_window=context_window,
        )

    async def create_conversation(self, title: str | None = None) -> UUID:  # noqa: F821
        """Create a new conversation."""
        from aura.infrastructure.database.models import Conversation

        conversation = Conversation(title=title)
        created = await self._conversation_repo.create(conversation)
        logger.info("conversation_created", conversation_id=created.id, title=title)
        return created.id

    async def send_message(
        self,
        conversation_id: UUID,  # noqa: F821
        user_message: str,
    ) -> str:
        """Send a user message and get an assistant response."""
        logger.info(
            "conversation_send_message",
            conversation_id=conversation_id,
            message_length=len(user_message),
        )

        # Store user message
        await self._message_repo.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER.value,
            content=user_message,
        )

        # Build context from recent messages
        context_messages = await self._build_context(conversation_id)

        # Create LLM request
        llm_request = LLMRequest(
            messages=context_messages,
            model="gemini-2.0-flash",  # Will be configurable later
        )

        # Get response from LLM
        response = await self._llm_service.generate(llm_request)

        # Store assistant message
        await self._message_repo.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT.value,
            content=response.content,
        )

        logger.info(
            "conversation_response_generated",
            conversation_id=conversation_id,
            response_length=len(response.content),
        )

        return response.content

    async def _build_context(self, conversation_id: UUID) -> list[Message]:  # noqa: F821
        """Build message context from recent conversation history."""
        db_messages = await self._message_repo.get_by_conversation(conversation_id)

        # Include system message + recent history
        system_message = Message(
            role=MessageRole.SYSTEM,
            content="You are Aura, a helpful AI assistant.",
        )

        context = [system_message]

        # Convert DB messages to core Message contracts
        recent = (
            db_messages[-self._context_window :]
            if len(db_messages) > self._context_window
            else db_messages
        )
        for msg in recent:
            context.append(
                Message(
                    role=MessageRole(msg.role),
                    content=msg.content,
                )
            )

        logger.debug(
            "context_built",
            conversation_id=conversation_id,
            message_count=len(context),
        )

        return context

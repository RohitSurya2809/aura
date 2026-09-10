from __future__ import annotations

from typing import TYPE_CHECKING

from aura.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from aura.core.llm_contracts import LLMRequest, ProviderResponse, StreamChunk
    from aura.infrastructure.providers.router import ProviderRouter


logger = get_logger(__name__)


class LLMService:
    """High-level LLM interaction service."""

    def __init__(self, router: ProviderRouter) -> None:
        self._router = router
        logger.info("llm_service_initialized")

    async def generate(self, request: LLMRequest) -> ProviderResponse:
        """Generate a response to an LLM request."""
        logger.info(
            "llm_service_generate",
            num_messages=len(request.messages),
            model=request.model,
        )

        try:
            response = await self._router.generate(request)
            logger.info("llm_service_generate_success", content_length=len(response.content))
            return response
        except Exception as exc:
            logger.error("llm_service_generate_failed", error=str(exc))
            raise

    async def stream(self, request: LLMRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream a response to an LLM request."""
        logger.info(
            "llm_service_stream",
            num_messages=len(request.messages),
            model=request.model,
        )

        chunk_count = 0
        try:
            async for chunk in self._router.stream(request):
                chunk_count += 1
                yield chunk
            logger.info("llm_service_stream_completed", chunk_count=chunk_count)
        except Exception as exc:
            logger.error("llm_service_stream_failed", error=str(exc), chunk_count=chunk_count)
            raise

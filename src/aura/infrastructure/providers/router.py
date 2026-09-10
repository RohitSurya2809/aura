from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from aura.core.errors import ProviderError
from aura.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from aura.core.llm_contracts import LLMRequest, ProviderResponse, StreamChunk
    from aura.infrastructure.providers.base import BaseProvider


logger = get_logger(__name__)


class ProviderPriority(StrEnum):
    """Provider priority for routing."""

    GEMINI = "gemini"
    OPENROUTER = "openrouter"


class ProviderRouter:
    """Routes LLM requests to the appropriate provider with fallback support."""

    def __init__(
        self,
        primary: BaseProvider,
        fallback: BaseProvider | None = None,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        logger.info(
            "provider_router_initialized",
            primary=primary.provider_name,
            fallback=fallback.provider_name if fallback else None,
        )

    async def generate(self, request: LLMRequest) -> ProviderResponse:
        """Generate response, with fallback if primary fails."""
        logger.info("provider_router_generate", primary=self._primary.provider_name)

        try:
            return await self._primary.generate(request)
        except ProviderError as exc:
            logger.warning(
                "primary_provider_failed",
                provider=self._primary.provider_name,
                error=str(exc),
            )

            if self._fallback:
                logger.info(
                    "attempting_fallback_provider",
                    fallback=self._fallback.provider_name,
                )
                try:
                    return await self._fallback.generate(request)
                except ProviderError as fallback_exc:
                    logger.error(
                        "fallback_provider_failed",
                        provider=self._fallback.provider_name,
                        error=str(fallback_exc),
                    )
                    raise ProviderError(
                        f"All providers failed: {str(exc)} | {str(fallback_exc)}"
                    ) from exc

            raise ProviderError(f"Primary provider failed: {str(exc)}") from exc

    async def stream(self, request: LLMRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream response, with fallback if primary fails."""
        logger.info("provider_router_stream", primary=self._primary.provider_name)

        try:
            async for chunk in self._primary.stream(request):
                yield chunk
        except ProviderError as exc:
            logger.warning(
                "primary_provider_failed_stream",
                provider=self._primary.provider_name,
                error=str(exc),
            )

            if self._fallback:
                logger.info(
                    "attempting_fallback_provider_stream",
                    fallback=self._fallback.provider_name,
                )
                try:
                    async for chunk in self._fallback.stream(request):
                        yield chunk
                except ProviderError as fallback_exc:
                    logger.error(
                        "fallback_provider_failed_stream",
                        provider=self._fallback.provider_name,
                        error=str(fallback_exc),
                    )
                    raise ProviderError(
                        f"All providers failed: {str(exc)} | {str(fallback_exc)}"
                    ) from exc
            else:
                raise ProviderError(f"Primary provider failed: {str(exc)}") from exc

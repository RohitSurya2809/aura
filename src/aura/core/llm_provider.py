from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from aura.core.llm_contracts import LLMRequest, ProviderResponse, StreamChunk


class LLMProvider(Protocol):
    """Abstract protocol for LLM providers.

    All providers (Gemini, OpenRouter, future additions) must implement this.
    """

    @property
    def provider_name(self) -> str:
        """Human-readable provider name (e.g., 'Gemini', 'OpenRouter')."""
        ...

    @property
    def is_available(self) -> bool:
        """Whether the provider is available (configuration valid, API key present)."""
        ...

    async def generate(
        self,
        request: LLMRequest,
    ) -> ProviderResponse:
        """Generate a single response from the LLM.

        Args:
            request: Canonical LLM request

        Returns:
            Canonical provider response

        Raises:
            ProviderError: For provider-level failures
            ValidationError: For invalid requests
        """
        ...

    async def stream(
        self,
        request: LLMRequest,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a response from the LLM.

        Args:
            request: Canonical LLM request

        Yields:
            StreamChunk objects

        Raises:
            ProviderError: For provider-level failures
        """
        ...

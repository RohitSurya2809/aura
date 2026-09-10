from __future__ import annotations

from collections.abc import AsyncGenerator  # noqa: TC003
from typing import TYPE_CHECKING

import google.generativeai as genai

from aura.core.config import GeminiSettings  # noqa: TC001
from aura.core.errors import ProviderError
from aura.core.llm_contracts import ProviderResponse, StreamChunk, Usage
from aura.core.logging import get_logger
from aura.infrastructure.providers.base import BaseProvider

if TYPE_CHECKING:
    from aura.core.llm_contracts import LLMRequest


logger = get_logger(__name__)


class GeminiProvider(BaseProvider):
    """Google Gemini LLM provider."""

    def __init__(self, settings: GeminiSettings) -> None:
        if not settings.is_configured:
            raise ProviderError("Gemini API key not configured")

        api_key = settings.api_key.get_secret_value()  # type: ignore[union-attr]
        genai.configure(api_key=api_key)  # type: ignore[attr-defined]

        super().__init__(model=settings.model)
        self._client = genai.GenerativeModel(self._model)  # type: ignore[attr-defined]
        logger.info("gemini_provider_initialized", model=self._model)

    @property
    def provider_name(self) -> str:
        return "Gemini"

    @property
    def is_available(self) -> bool:
        return True

    async def generate(self, request: LLMRequest) -> ProviderResponse:
        """Generate response using Gemini."""
        try:
            messages = self._messages_to_provider_format(request.messages)

            response = self._client.generate_content(
                messages,
                request_options={"timeout": self._timeout},
            )

            usage = None
            if hasattr(response, "usage_metadata"):
                metadata = response.usage_metadata
                usage = Usage(
                    input_tokens=getattr(metadata, "prompt_token_count", 0),
                    output_tokens=getattr(metadata, "candidates_token_count", 0),
                )

            logger.info(
                "gemini_response_generated",
                usage=usage,
                finish_reason=response.candidates[0].finish_reason if response.candidates else None,
            )

            stop_reason = None
            if response.candidates:
                stop_reason = str(response.candidates[0].finish_reason)

            return ProviderResponse(
                content=response.text,
                usage=usage,
                stop_reason=stop_reason,
            )
        except Exception as exc:
            logger.error("gemini_generation_failed", error=str(exc))
            raise ProviderError(f"Gemini generation failed: {exc}") from exc

    def stream(self, request: LLMRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream response using Gemini."""
        return self._stream(request)

    async def _stream(self, request: LLMRequest) -> AsyncGenerator[StreamChunk, None]:
        """Actual streaming implementation."""
        try:
            messages = self._messages_to_provider_format(request.messages)

            response = self._client.generate_content(
                messages,
                stream=True,
                request_options={"timeout": self._timeout},
            )

            for chunk in response:
                if chunk.text:
                    yield StreamChunk(delta=chunk.text)

            logger.info("gemini_stream_completed")
        except Exception as exc:
            logger.error("gemini_stream_failed", error=str(exc))
            raise ProviderError(f"Gemini streaming failed: {exc}") from exc

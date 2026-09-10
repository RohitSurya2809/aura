from __future__ import annotations

import json
from collections.abc import AsyncGenerator  # noqa: TC003
from typing import TYPE_CHECKING

import httpx

from aura.core.config import OpenRouterSettings  # noqa: TC001
from aura.core.errors import ProviderError
from aura.core.llm_contracts import ProviderResponse, StreamChunk, Usage
from aura.core.logging import get_logger
from aura.infrastructure.providers.base import BaseProvider

if TYPE_CHECKING:
    from aura.core.llm_contracts import LLMRequest


logger = get_logger(__name__)


class OpenRouterProvider(BaseProvider):
    """OpenRouter LLM provider."""

    def __init__(self, settings: OpenRouterSettings) -> None:
        if not settings.is_configured:
            raise ProviderError("OpenRouter API key not configured")

        self._api_key = settings.api_key.get_secret_value()  # type: ignore[union-attr]
        self._base_url = getattr(settings, "base_url", "https://openrouter.ai/api/v1")

        super().__init__(model=settings.model)
        logger.info("openrouter_provider_initialized", model=self._model)

    @property
    def provider_name(self) -> str:
        return "OpenRouter"

    @property
    def is_available(self) -> bool:
        return True

    async def generate(self, request: LLMRequest) -> ProviderResponse:
        """Generate response using OpenRouter."""
        try:
            messages = self._messages_to_provider_format(request.messages)

            payload = {
                "model": self._model,
                "messages": messages,
                "temperature": request.temperature or 0.7,
            }
            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens

            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "HTTP-Referer": "https://github.com/RohitSurya2809/aura",
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            usage = None
            if "usage" in data:
                usage = Usage(
                    input_tokens=data["usage"].get("prompt_tokens", 0),
                    output_tokens=data["usage"].get("completion_tokens", 0),
                )

            content = data["choices"][0]["message"]["content"]
            stop_reason = data["choices"][0].get("finish_reason")

            logger.info(
                "openrouter_response_generated",
                usage=usage,
                finish_reason=stop_reason,
            )

            return ProviderResponse(
                content=content,
                usage=usage,
                stop_reason=stop_reason,
            )
        except Exception as exc:
            logger.error("openrouter_generation_failed", error=str(exc))
            raise ProviderError(f"OpenRouter generation failed: {exc}") from exc

    def stream(self, request: LLMRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream response using OpenRouter."""
        return self._stream(request)

    async def _stream(self, request: LLMRequest) -> AsyncGenerator[StreamChunk, None]:
        """Actual streaming implementation."""
        try:
            messages = self._messages_to_provider_format(request.messages)

            payload = {
                "model": self._model,
                "messages": messages,
                "stream": True,
                "temperature": request.temperature or 0.7,
            }
            if request.max_tokens:
                payload["max_tokens"] = request.max_tokens

            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "HTTP-Referer": "https://github.com/RohitSurya2809/aura",
            }

            async with (
                httpx.AsyncClient(timeout=self._timeout) as client,
                client.stream(
                    "POST",
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as response,
            ):
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        data = json.loads(data_str)
                        delta = data["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield StreamChunk(delta=delta)

            logger.info("openrouter_stream_completed")
        except Exception as exc:
            logger.error("openrouter_stream_failed", error=str(exc))
            raise ProviderError(f"OpenRouter streaming failed: {exc}") from exc

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator  # noqa: TC003
from typing import TYPE_CHECKING

from aura.core.logging import get_logger

if TYPE_CHECKING:
    from aura.core.llm_contracts import LLMRequest, ProviderResponse, StreamChunk


logger = get_logger(__name__)


class BaseProvider(ABC):
    """Base class for LLM provider implementations."""

    def __init__(self, model: str, timeout: float = 30.0) -> None:
        self._model = model
        self._timeout = timeout

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return self.__class__.__name__

    @property
    def model(self) -> str:
        return self._model

    @abstractmethod
    async def generate(self, request: LLMRequest) -> ProviderResponse:
        """Generate response. Subclasses must implement."""
        ...

    @abstractmethod
    def stream(self, request: LLMRequest) -> AsyncGenerator[StreamChunk, None]:
        """Stream response. Subclasses must implement."""
        ...

    @staticmethod
    def _messages_to_provider_format(messages: list) -> list[dict[str, str]]:  # type: ignore[type-arg]
        """Convert canonical messages to provider format."""
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]

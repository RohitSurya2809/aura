from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MessageRole(StrEnum):
    """Canonical message role enumeration."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    # Future: TOOL = "tool", FUNCTION = "function", DEVELOPER = "developer"


@dataclass(frozen=True)
class Message:
    """Canonical internal message representation."""

    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Message content cannot be empty")


@dataclass(frozen=True)
class Usage:
    """Token usage information (provider-agnostic)."""

    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class ProviderResponse:
    """Canonical response from any LLM provider."""

    content: str
    role: MessageRole = MessageRole.ASSISTANT
    usage: Usage | None = None
    stop_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Response content cannot be empty")


@dataclass(frozen=True)
class LLMRequest:
    """Canonical LLM request (provider-agnostic)."""

    messages: list[Message]
    model: str
    temperature: float | None = None
    max_tokens: int | None = None

    def __post_init__(self) -> None:
        if not self.messages:
            raise ValueError("Request must include at least one message")


@dataclass(frozen=True)
class StreamChunk:
    """A streaming response chunk from an LLM provider."""

    delta: str
    stop_reason: str | None = None
    usage: Usage | None = None

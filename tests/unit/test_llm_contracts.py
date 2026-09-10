from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from aura.core.llm_contracts import (
    LLMRequest,
    Message,
    MessageRole,
    ProviderResponse,
    StreamChunk,
    Usage,
)


class TestMessageRole:
    def test_roles_exist(self) -> None:
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"


class TestMessage:
    def test_message_creation(self) -> None:
        msg = Message(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"

    def test_message_immutable(self) -> None:
        msg = Message(role=MessageRole.USER, content="Hello")
        with pytest.raises(FrozenInstanceError):
            msg.content = "Goodbye"  # type: ignore[misc]

    def test_message_empty_content_raises(self) -> None:
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message(role=MessageRole.USER, content="")


class TestUsage:
    def test_usage_creation(self) -> None:
        usage = Usage(input_tokens=10, output_tokens=20)
        assert usage.input_tokens == 10
        assert usage.output_tokens == 20
        assert usage.total_tokens == 30


class TestProviderResponse:
    def test_response_creation(self) -> None:
        response = ProviderResponse(content="Hello")
        assert response.content == "Hello"
        assert response.role == MessageRole.ASSISTANT

    def test_response_with_usage(self) -> None:
        usage = Usage(input_tokens=10, output_tokens=5)
        response = ProviderResponse(content="Hi", usage=usage)
        assert response.usage == usage

    def test_response_empty_content_raises(self) -> None:
        with pytest.raises(ValueError, match="Response content cannot be empty"):
            ProviderResponse(content="")


class TestLLMRequest:
    def test_request_creation(self) -> None:
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are helpful"),
            Message(role=MessageRole.USER, content="Hi"),
        ]
        request = LLMRequest(messages=messages, model="test-model")
        assert request.messages == messages
        assert request.model == "test-model"

    def test_request_empty_messages_raises(self) -> None:
        with pytest.raises(ValueError, match="Request must include at least one message"):
            LLMRequest(messages=[], model="test-model")

    def test_request_with_temperature(self) -> None:
        messages = [Message(role=MessageRole.USER, content="Hi")]
        request = LLMRequest(
            messages=messages,
            model="test-model",
            temperature=0.5,
        )
        assert request.temperature == 0.5


class TestStreamChunk:
    def test_chunk_creation(self) -> None:
        chunk = StreamChunk(delta="Hello")
        assert chunk.delta == "Hello"
        assert chunk.stop_reason is None

    def test_chunk_with_stop_reason(self) -> None:
        chunk = StreamChunk(delta=".", stop_reason="stop_sequence")
        assert chunk.stop_reason == "stop_sequence"

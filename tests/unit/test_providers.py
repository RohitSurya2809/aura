from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from aura.core.config import GeminiSettings, OpenRouterSettings
from aura.core.errors import ProviderError
from aura.core.llm_contracts import LLMRequest, Message, MessageRole
from aura.infrastructure.providers.gemini import GeminiProvider
from aura.infrastructure.providers.openrouter import OpenRouterProvider


class TestGeminiProvider:
    @pytest.fixture
    def gemini_settings(self) -> GeminiSettings:
        return GeminiSettings(api_key=SecretStr("test-key"))

    def test_initialization(self, gemini_settings: GeminiSettings) -> None:
        with patch("aura.infrastructure.providers.gemini.genai"):
            provider = GeminiProvider(gemini_settings)
            assert provider.provider_name == "Gemini"
            assert provider.is_available is True

    def test_not_configured_raises(self) -> None:
        settings = GeminiSettings(api_key=None)
        with pytest.raises(ProviderError):
            GeminiProvider(settings)

    @pytest.mark.asyncio
    async def test_generate(self, gemini_settings: GeminiSettings) -> None:
        with patch("aura.infrastructure.providers.gemini.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "Hello response"
            mock_response.candidates = [MagicMock(finish_reason="STOP")]

            mock_client = MagicMock()
            mock_client.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_client

            provider = GeminiProvider(gemini_settings)
            request = LLMRequest(
                messages=[Message(role=MessageRole.USER, content="Hello")],
                model="test-model",
            )

            response = await provider.generate(request)

            assert response.content == "Hello response"
            assert response.role == MessageRole.ASSISTANT


class TestOpenRouterProvider:
    @pytest.fixture
    def openrouter_settings(self) -> OpenRouterSettings:
        return OpenRouterSettings(api_key=SecretStr("test-key"))

    def test_initialization(self, openrouter_settings: OpenRouterSettings) -> None:
        provider = OpenRouterProvider(openrouter_settings)
        assert provider.provider_name == "OpenRouter"
        assert provider.is_available is True

    def test_not_configured_raises(self) -> None:
        settings = OpenRouterSettings(api_key=None)
        with pytest.raises(ProviderError):
            OpenRouterProvider(settings)

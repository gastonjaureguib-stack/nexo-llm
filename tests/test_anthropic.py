
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from anthropic import (
    AuthenticationError,
    APIConnectionError,
    RateLimitError,
    InternalServerError,
)

from nexo_llm.anthropic_client import AnthropicClient
from nexo_llm.schemas import ChatMessage, ModelConfig
from nexo_llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMAPIError,
)


class TestAnthropicClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.enterContext(patch("nexo_llm.anthropic_client.AsyncAnthropic", autospec=True))
        self.client = AnthropicClient(
            api_key="clave-de-prueba"
        )

        self.messages = [
            ChatMessage(
                role="user",
                content="¿Qué es la entropía?"
            )
        ]

        self.config = ModelConfig(
            model="modelo-de-prueba",
            temperature=0.7,
            max_tokens=100
        )

    def create_response(self, status_code):
        response = MagicMock()
        response.status_code = status_code
        return response

    async def test_authentication_error(self):
        error = AuthenticationError(
            "Credenciales inválidas",
            response=self.create_response(401),
            body=None
        )

        self.client.client.messages.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMAuthenticationError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_rate_limit_error(self):
        error = RateLimitError(
            "Límite de solicitudes alcanzado",
            response=self.create_response(429),
            body=None
        )

        self.client.client.messages.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMRateLimitError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_connection_error(self):
        error = APIConnectionError(
            request=MagicMock()
        )

        self.client.client.messages.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMConnectionError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_api_error(self):
        error = InternalServerError(
            "Error interno del proveedor",
            response=self.create_response(500),
            body=None
        )

        self.client.client.messages.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMAPIError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_stream_authentication_error(self):
        error = AuthenticationError(
            "Credenciales inválidas",
            response=self.create_response(401),
            body=None
        )

        stream_context = MagicMock()
        stream_context.__aenter__ = AsyncMock(
            side_effect=error
        )
        stream_context.__aexit__ = AsyncMock(
            return_value=False
        )

        self.client.client.messages.stream = MagicMock(
            return_value=stream_context
        )

        with self.assertRaises(LLMAuthenticationError):
            async for fragment in self.client.stream(
                self.messages,
                self.config
            ):
                pass

    async def test_generate_success(self):
        response = SimpleNamespace(
            model="modelo-de-prueba",
            content=[
                SimpleNamespace(type="text", text="La entropía mide "),
                SimpleNamespace(type="tool_use"),
                SimpleNamespace(type="text", text="la incertidumbre."),
            ]
        )

        self.client.client.messages.create = AsyncMock(
            return_value=response
        )

        result = await self.client.generate(
            self.messages,
            self.config
        )

        self.assertEqual(
            result.provider,
            "anthropic"
        )

        self.assertEqual(
            result.model,
            "modelo-de-prueba"
        )

        self.assertEqual(
            result.content,
            "La entropía mide la incertidumbre."
        )

        self.client.client.messages.create.assert_awaited_once()

    async def test_stream_success(self):

        async def mock_text_stream():
            yield "La entropía "
            yield "mide la incertidumbre."

        stream_response = SimpleNamespace(text_stream=mock_text_stream())

        stream_context = MagicMock()
        stream_context.__aenter__ = AsyncMock(
            return_value=stream_response
        )
        stream_context.__aexit__ = AsyncMock(
            return_value=False
        )

        self.client.client.messages.stream = MagicMock(
            return_value=stream_context
        )

        fragments = []

        async for fragment in self.client.stream(
            self.messages,
            self.config
        ):
            fragments.append(fragment)

        self.assertEqual(
            fragments,
            [
                "La entropía ",
                "mide la incertidumbre."
            ]
        )

        self.assertEqual(
            "".join(fragments),
            "La entropía mide la incertidumbre."
        )

        self.client.client.messages.stream.assert_called_once()
        stream_context.__aenter__.assert_awaited_once()
        stream_context.__aexit__.assert_awaited_once_with(None, None, None)


if __name__ == "__main__":
    unittest.main()

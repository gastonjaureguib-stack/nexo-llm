
import unittest
from types import SimpleNamespace

from unittest.mock import AsyncMock, MagicMock, patch

from openai import (
    AuthenticationError,
    APIConnectionError,
    RateLimitError,
    InternalServerError,
)

from nexo_llm.openai_client import OpenAIClient
from nexo_llm.schemas import ChatMessage, ModelConfig

from nexo_llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMAPIError,
)


class TestOpenAIClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.enterContext(patch("nexo_llm.openai_client.AsyncOpenAI"))
        self.client = OpenAIClient(
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

    async def test_authentication_error(self):
        response = MagicMock()
        response.status_code = 401

        error = AuthenticationError(
            "Credenciales inválidas",
            response=response,
            body=None
        )

        self.client.client.chat.completions.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMAuthenticationError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_rate_limit_error(self):
        response = MagicMock()
        response.status_code = 429

        error = RateLimitError(
            "Límite de solicitudes alcanzado",
            response=response,
            body=None
        )

        self.client.client.chat.completions.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMRateLimitError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_connection_error(self):
        request = MagicMock()

        error = APIConnectionError(
            request=request
        )

        self.client.client.chat.completions.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMConnectionError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_api_error(self):
        response = MagicMock()
        response.status_code = 500

        error = InternalServerError(
            "Error interno del proveedor",
            response=response,
            body=None
        )

        self.client.client.chat.completions.create = AsyncMock(
            side_effect=error
        )

        with self.assertRaises(LLMAPIError):
            await self.client.generate(
                self.messages,
                self.config
            )

    async def test_stream_authentication_error(self):
        response = MagicMock()
        response.status_code = 401

        error = AuthenticationError(
            "Credenciales inválidas",
            response=response,
            body=None
        )

        self.client.client.chat.completions.create = AsyncMock(
            side_effect=error
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
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="La entropía mide la incertidumbre.")
                )
            ]
        )

        self.client.client.chat.completions.create = AsyncMock(
            return_value=response
        )

        result = await self.client.generate(
            self.messages,
            self.config
        )

        self.assertEqual(result.provider, "openai")
        self.assertEqual(result.model, "modelo-de-prueba")
        self.assertEqual(
            result.content,
            "La entropía mide la incertidumbre."
        )

        self.client.client.chat.completions.create.assert_awaited_once()

    async def test_stream_success(self):

        async def mock_stream():
            yield SimpleNamespace(choices=[])
            for content in [
                "La entropía ",
                None,
                "mide la incertidumbre."
            ]:
                yield SimpleNamespace(
                    choices=[SimpleNamespace(delta=SimpleNamespace(content=content))]
                )

        self.client.client.chat.completions.create = AsyncMock(
            return_value=mock_stream()
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

        self.client.client.chat.completions.create.assert_awaited_once_with(
            model=self.config.model,
            messages=[message.model_dump() for message in self.messages],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True
        )


if __name__ == "__main__":
    unittest.main()

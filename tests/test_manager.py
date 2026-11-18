
import unittest

from unittest.mock import AsyncMock, patch

from nexo_llm.manager import AsyncLLMManager
from nexo_llm.openai_client import OpenAIClient
from nexo_llm.anthropic_client import AnthropicClient
from nexo_llm.schemas import ChatMessage, ModelConfig, ModelResponse


class TestAsyncLLMManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.enterContext(patch("nexo_llm.openai_client.AsyncOpenAI", autospec=True))
        self.enterContext(patch("nexo_llm.anthropic_client.AsyncAnthropic", autospec=True))

    def test_select_openai(self):
        manager = AsyncLLMManager(
            provider="openai",
            api_key="clave-de-prueba"
        )

        self.assertIsInstance(
            manager.client,
            OpenAIClient
        )

    def test_select_anthropic(self):
        manager = AsyncLLMManager(
            provider="anthropic",
            api_key="clave-de-prueba"
        )

        self.assertIsInstance(
            manager.client,
            AnthropicClient
        )

    def test_reject_unknown_provider(self):
        with self.assertRaises(ValueError):
            AsyncLLMManager(
                provider="proveedor-inexistente",
                api_key="clave-de-prueba"
            )

    async def test_generate_async(self):
        manager = AsyncLLMManager(
            provider="openai",
            api_key="clave-de-prueba"
        )

        messages = [
            ChatMessage(
                role="user",
                content="¿Qué es la entropía?"
            )
        ]

        config = ModelConfig(
            model="modelo-de-prueba",
            temperature=0.7,
            max_tokens=100
        )

        expected_response = ModelResponse(
            provider="openai",
            model="modelo-de-prueba",
            content="La entropía es una medida de incertidumbre."
        )

        manager.client.generate = AsyncMock(
            return_value=expected_response
        )

        result = await manager.generate(messages, config)

        self.assertEqual(result, expected_response)

        manager.client.generate.assert_awaited_once_with(
            messages,
            config
        )

    async def test_stream_async(self):
        manager = AsyncLLMManager(
            provider="openai",
            api_key="clave-de-prueba"
        )

        messages = [
            ChatMessage(
                role="user",
                content="¿Qué es la entropía?"
            )
        ]

        config = ModelConfig(
            model="modelo-de-prueba",
            temperature=0.7,
            max_tokens=100
        )

        async def simulated_stream(messages, config):
            yield "La entropía "
            yield "mide la "
            yield "incertidumbre."

        manager.client.stream = simulated_stream

        fragments = []

        async for fragment in manager.stream(messages, config):
            fragments.append(fragment)

        self.assertEqual(
            fragments,
            [
                "La entropía ",
                "mide la ",
                "incertidumbre."
            ]
        )

        self.assertEqual(
            "".join(fragments),
            "La entropía mide la incertidumbre."
        )


if __name__ == "__main__":
    unittest.main()

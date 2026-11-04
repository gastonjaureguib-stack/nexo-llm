
from collections.abc import AsyncIterator

from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .schemas import ChatMessage, ModelConfig, ModelResponse


class AsyncLLMManager:

    def __init__(self, provider: str, api_key: str):

        if provider == "openai":
            self.client: BaseLLMClient = OpenAIClient(
                api_key=api_key
            )

        elif provider == "anthropic":
            self.client = AnthropicClient(
                api_key=api_key
            )

        else:
            raise ValueError(
                f"Proveedor no soportado: {provider}"
            )

    async def generate(
        self,
        messages: list[ChatMessage],
        config: ModelConfig
    ) -> ModelResponse:

        return await self.client.generate(messages, config)

    async def stream(
        self,
        messages: list[ChatMessage],
        config: ModelConfig
    ) -> AsyncIterator[str]:

        async for fragment in self.client.stream(messages, config):
            yield fragment

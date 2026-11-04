
from collections.abc import AsyncIterator

from anthropic import (
    AsyncAnthropic,
    AuthenticationError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    APIStatusError,
)

from .base_client import BaseLLMClient
from .schemas import ChatMessage, ModelConfig, ModelResponse

from .exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMAPIError,
)


class AnthropicClient(BaseLLMClient):

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        messages: list[ChatMessage],
        config: ModelConfig
    ) -> ModelResponse:

        system_messages = [
            message.content
            for message in messages
            if message.role == "system"
        ]

        chat_messages = [
            message.model_dump()
            for message in messages
            if message.role != "system"
        ]

        try:
            response = await self.client.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                system="\n".join(system_messages),
                messages=chat_messages
            )

            content = "".join(
                block.text
                for block in response.content
                if block.type == "text"
            )

            return ModelResponse(
                provider="anthropic",
                model=response.model,
                content=content
            )

        except AuthenticationError as error:
            raise LLMAuthenticationError(
                "Anthropic rechazó las credenciales."
            ) from error

        except RateLimitError as error:
            raise LLMRateLimitError(
                "Anthropic alcanzó un límite de solicitudes."
            ) from error

        except (APIConnectionError, APITimeoutError) as error:
            raise LLMConnectionError(
                "No fue posible conectar con Anthropic."
            ) from error

        except APIStatusError as error:
            raise LLMAPIError(
                f"Anthropic devolvió un error HTTP {error.status_code}."
            ) from error

    async def stream(
        self,
        messages: list[ChatMessage],
        config: ModelConfig
    ) -> AsyncIterator[str]:

        system_messages = [
            message.content
            for message in messages
            if message.role == "system"
        ]

        chat_messages = [
            message.model_dump()
            for message in messages
            if message.role != "system"
        ]

        try:
            async with self.client.messages.stream(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                system="\n".join(system_messages),
                messages=chat_messages
            ) as response:

                async for text in response.text_stream:
                    yield text

        except AuthenticationError as error:
            raise LLMAuthenticationError(
                "Anthropic rechazó las credenciales."
            ) from error

        except RateLimitError as error:
            raise LLMRateLimitError(
                "Anthropic alcanzó un límite de solicitudes."
            ) from error

        except (APIConnectionError, APITimeoutError) as error:
            raise LLMConnectionError(
                "No fue posible conectar con Anthropic."
            ) from error

        except APIStatusError as error:
            raise LLMAPIError(
                f"Anthropic devolvió un error HTTP {error.status_code}."
            ) from error

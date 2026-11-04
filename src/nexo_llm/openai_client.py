
from collections.abc import AsyncIterator

from openai import (
    AsyncOpenAI,
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


class OpenAIClient(BaseLLMClient):

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        messages: list[ChatMessage],
        config: ModelConfig
    ) -> ModelResponse:

        try:
            response = await self.client.chat.completions.create(
                model=config.model,
                messages=[
                    message.model_dump()
                    for message in messages
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

            return ModelResponse(
                provider="openai",
                model=response.model,
                content=response.choices[0].message.content or ""
            )

        except AuthenticationError as error:
            raise LLMAuthenticationError(
                "OpenAI rechazó las credenciales."
            ) from error

        except RateLimitError as error:
            raise LLMRateLimitError(
                "OpenAI alcanzó un límite de solicitudes o cuota."
            ) from error

        except (APIConnectionError, APITimeoutError) as error:
            raise LLMConnectionError(
                "No fue posible conectar con OpenAI."
            ) from error

        except APIStatusError as error:
            raise LLMAPIError(
                f"OpenAI devolvió un error HTTP {error.status_code}."
            ) from error

    async def stream(
        self,
        messages: list[ChatMessage],
        config: ModelConfig
    ) -> AsyncIterator[str]:

        try:
            response = await self.client.chat.completions.create(
                model=config.model,
                messages=[
                    message.model_dump()
                    for message in messages
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                stream=True
            )

            async for chunk in response:
                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:
                    yield content

        except AuthenticationError as error:
            raise LLMAuthenticationError(
                "OpenAI rechazó las credenciales."
            ) from error

        except RateLimitError as error:
            raise LLMRateLimitError(
                "OpenAI alcanzó un límite de solicitudes o cuota."
            ) from error

        except (APIConnectionError, APITimeoutError) as error:
            raise LLMConnectionError(
                "No fue posible conectar con OpenAI."
            ) from error

        except APIStatusError as error:
            raise LLMAPIError(
                f"OpenAI devolvió un error HTTP {error.status_code}."
            ) from error

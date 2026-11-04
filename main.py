
import asyncio
import os

from dotenv import load_dotenv

from nexo_llm.manager import AsyncLLMManager
from nexo_llm.schemas import ChatMessage, ModelConfig

from nexo_llm.exceptions import (
    LLMError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMAPIError,
)


async def main():
    load_dotenv()

    provider = os.getenv("LLM_PROVIDER", "").strip().lower()

    if provider not in ("openai", "anthropic"):
        print("Nexo LLM | Proveedor no válido.")
        return

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_MODEL")
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model_name = os.getenv("ANTHROPIC_MODEL")

    if not api_key or not api_key.strip():
        print(f"Nexo LLM | Falta configurar la clave de {provider}.")
        return

    if not model_name or not model_name.strip():
        print(f"Nexo LLM | Falta configurar el modelo de {provider}.")
        return

    manager = AsyncLLMManager(
        provider=provider,
        api_key=api_key
    )

    messages = [
        ChatMessage(
            role="user",
            content="¿Qué es la entropía?"
        )
    ]

    config = ModelConfig(
        model=model_name.strip(),
        temperature=0.7,
        max_tokens=500
    )

    print("\n=== NEXO LLM ===")
    print(f"Proveedor: {provider}")
    print(f"Modelo: {config.model}")
    print(f"Pregunta: {messages[0].content}")

    try:
        print("\n--- Generación normal ---")

        response = await manager.generate(messages, config)
        print(response.content)

        print("\n--- Generación streaming ---")

        async for fragment in manager.stream(messages, config):
            print(fragment, end="", flush=True)

        print("\n\n=== Fin de la ejecución ===")

    except LLMAuthenticationError:
        print("\nNexo LLM | Error: credenciales inválidas.")

    except LLMRateLimitError:
        print("\nNexo LLM | Error: límite de solicitudes o cuota alcanzada.")

    except LLMConnectionError:
        print("\nNexo LLM | Error: no fue posible conectar con el proveedor.")

    except LLMAPIError as error:
        print(f"\nNexo LLM | Error de API: {error}")

    except LLMError as error:
        print(f"\nNexo LLM | Error: {error}")


if __name__ == "__main__":
    asyncio.run(main())

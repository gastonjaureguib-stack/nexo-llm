
import asyncio
import logging

from nexo_pipeline.chain import process_text


async def main():
    texto = (
        "El servidor Node.js dejó de responder. "
        "La API devuelve errores 500 y los usuarios "
        "no pueden acceder al sistema."
    )

    resultado = await process_text(texto)

    print(resultado.model_dump_json(indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
    asyncio.run(main())

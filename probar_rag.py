import asyncio

from nexo_rag.chain import get_rag_response


async def main():
    print("Nexo Intelligence. Escribí salir para finalizar.")
    while True:
        try:
            pregunta = input("Pregunta: ").strip()
        except EOFError:
            return
        if pregunta.lower() == "salir":
            return
        if not pregunta:
            print("La consulta no puede estar vacía.")
            continue

        try:
            resultado = await get_rag_response(pregunta)
        except Exception as error:
            print(f"No se pudo procesar la consulta ({type(error).__name__}).")
            continue

        print(resultado.respuesta)
        for referencia in resultado.referencias:
            print(f"- {referencia}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

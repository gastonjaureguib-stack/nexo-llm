from nexo_rag.ingestion import ingerir_documentos


def main():
    try:
        resultado = ingerir_documentos()
    except (OSError, ValueError) as error:
        print(f"Ingesta fallida ({type(error).__name__}). Revisá los archivos y la configuración.")
        return 1
    except Exception as error:
        print(f"Ingesta fallida ({type(error).__name__}). Revisá el acceso a ChromaDB y OpenAI.")
        return 1

    print(f"Documentos encontrados: {resultado.encontrados}")
    print(f"Documentos vacíos omitidos: {resultado.vacios}")
    print(f"Documentos procesados: {resultado.procesados}")
    print(f"Documentos previamente indexados: {resultado.previamente_indexados}")
    print(f"Fragmentos generados: {resultado.fragmentos_generados}")
    print(f"Fragmentos nuevos: {resultado.fragmentos_nuevos}")
    print(f"Fragmentos eliminados: {resultado.fragmentos_eliminados}")
    print(f"Fragmentos almacenados: {resultado.fragmentos_almacenados}")
    print("Ingesta completada." if resultado.fragmentos_almacenados else "Ingesta completada. La colección está vacía.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

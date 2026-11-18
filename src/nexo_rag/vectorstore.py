from contextlib import contextmanager

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import COLLECTION_NAME, EMBEDDING_MODEL, ENV_FILE, PERSIST_DIRECTORY


def crear_embeddings():
    load_dotenv(ENV_FILE)
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


@contextmanager
def abrir_vectorstore(directorio=PERSIST_DIRECTORY, *, embeddings=None, crear=True):
    with chromadb.PersistentClient(
        path=str(directorio.resolve()),
        settings=Settings(
            _env_file=None,
            anonymized_telemetry=False,
            chroma_otel_granularity="none",
        ),
    ) as cliente:
        if crear:
            coleccion = cliente.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=None,
                metadata={"embedding_model": EMBEDDING_MODEL},
                configuration={"hnsw": {"space": "cosine"}},
            )
        else:
            coleccion = cliente.get_collection(COLLECTION_NAME, embedding_function=None)

        if (
            (coleccion.metadata or {}).get("embedding_model") != EMBEDDING_MODEL
            or (coleccion.configuration_json.get("hnsw") or {}).get("space") != "cosine"
        ):
            raise ValueError("La colección no usa el modelo de embeddings o la métrica configurados.")

        yield Chroma(
            client=cliente,
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            create_collection_if_not_exists=False,
        )

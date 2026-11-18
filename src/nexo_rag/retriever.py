import asyncio
from contextlib import ExitStack

from chromadb.errors import NotFoundError
from langchain_core.documents import Document

from .config import PERSIST_DIRECTORY, TOP_K
from .vectorstore import abrir_vectorstore, crear_embeddings


def validar_consulta(query: str) -> str:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("La consulta no puede estar vacía.")
    return query.strip()


def _recuperar(query, directorio, embeddings):
    if not directorio.exists():
        return []

    with ExitStack() as recursos:
        try:
            almacen = recursos.enter_context(abrir_vectorstore(directorio, crear=False))
        except NotFoundError:
            return []
        if not almacen.get(limit=1, include=[])["ids"]:
            return []
        if embeddings is None:
            embeddings = crear_embeddings()
        vector = embeddings.embed_query(query)
        return almacen.similarity_search_by_vector(vector, k=TOP_K)


async def recuperar_documentos(
    query: str, *, directorio=PERSIST_DIRECTORY, embeddings=None
) -> list[Document]:
    return await asyncio.to_thread(_recuperar, validar_consulta(query), directorio, embeddings)

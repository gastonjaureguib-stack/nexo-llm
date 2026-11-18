import hashlib
import json
from bisect import bisect_left, bisect_right
from contextlib import ExitStack
from dataclasses import dataclass
from itertools import accumulate, chain

import tiktoken
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_DIRECTORY, MIN_CHUNK_SIZE, PERSIST_DIRECTORY, TOKEN_ENCODING
from .vectorstore import abrir_vectorstore, crear_embeddings


@dataclass(frozen=True)
class ResultadoIngesta:
    encontrados: int
    vacios: int
    procesados: int
    previamente_indexados: int
    fragmentos_generados: int
    fragmentos_nuevos: int
    fragmentos_eliminados: int
    fragmentos_almacenados: int


def leer_documentos(directorio=DATA_DIRECTORY):
    directorio = directorio.resolve(strict=True)
    if not directorio.is_dir():
        raise NotADirectoryError(directorio)

    documentos = []
    vacios = 0
    for ruta in sorted(directorio.iterdir()):
        if ruta.suffix.lower() not in {".txt", ".md"} or ruta.is_symlink() or not ruta.is_file():
            continue
        try:
            texto = ruta.read_text(encoding="utf-8-sig").strip()
        except (OSError, UnicodeError) as error:
            raise ValueError(f"No se pudo leer el documento {ruta.name}.") from error
        if not texto:
            vacios += 1
            continue
        documentos.append(Document(
            page_content=texto,
            metadata={"archivo": ruta.name, "origen": ruta.relative_to(directorio).as_posix()},
        ))
    return documentos, vacios


def _dividir_texto(texto, separador, encoding):
    tokens = encoding.encode(texto, disallowed_special=())
    if not tokens:
        return []

    _, offsets = encoding.decode_with_offsets(tokens)
    offsets.append(len(texto))
    naturales = [
        bisect_left(offsets, posicion)
        for posicion in accumulate(map(len, separador.split_text(texto)))
    ]
    partes = []
    inicio = 0
    while len(tokens) - inicio > CHUNK_SIZE:
        minimo = inicio + MIN_CHUNK_SIZE
        if len(tokens) - inicio <= 2 * CHUNK_SIZE - CHUNK_OVERLAP:
            minimo = max(minimo, len(tokens) - CHUNK_SIZE + CHUNK_OVERLAP)
        maximo = min(inicio + CHUNK_SIZE, len(tokens) - MIN_CHUNK_SIZE + CHUNK_OVERLAP)
        cortes = naturales[bisect_left(naturales, minimo):bisect_right(naturales, maximo)]
        for fin in chain(reversed(cortes), range(maximo, minimo - 1, -1)):
            siguiente = fin - CHUNK_OVERLAP
            if offsets[fin] == offsets[fin - 1] or offsets[siguiente] == offsets[siguiente - 1]:
                continue
            parte = texto[offsets[inicio]:offsets[fin]]
            overlap = texto[offsets[siguiente]:offsets[fin]]
            if (
                MIN_CHUNK_SIZE <= len(encoding.encode(parte, disallowed_special=())) <= CHUNK_SIZE
                and len(encoding.encode(overlap, disallowed_special=())) == CHUNK_OVERLAP
            ):
                partes.append((inicio, parte))
                inicio = siguiente
                break
        else:
            break

    final = texto[offsets[inicio]:]
    if partes and len(encoding.encode(final, disallowed_special=())) < MIN_CHUNK_SIZE:
        inicio, _ = partes.pop()
        final = texto[offsets[inicio]:]
    return [parte for _, parte in partes] + [final]


def fragmentar_documentos(documentos):
    if not documentos:
        return []

    separador = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name=TOKEN_ENCODING,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=0,
        strip_whitespace=False,
        disallowed_special=(),
    )
    encoding = tiktoken.get_encoding(TOKEN_ENCODING)
    fragmentos = []
    for documento in documentos:
        for indice, texto in enumerate(_dividir_texto(documento.page_content, separador, encoding)):
            datos_id = json.dumps([documento.metadata["origen"], indice, texto], ensure_ascii=False)
            identificador = hashlib.sha256(datos_id.encode("utf-8")).hexdigest()
            fragmentos.append(Document(
                id=identificador,
                page_content=texto,
                metadata={**documento.metadata, "indice": indice, "id": identificador},
            ))
    return fragmentos


def ingerir_documentos(directorio=DATA_DIRECTORY, destino=PERSIST_DIRECTORY, *, embeddings=None):
    documentos, vacios = leer_documentos(directorio)
    fragmentos = fragmentar_documentos(documentos)
    with ExitStack() as recursos:
        almacen = recursos.enter_context(abrir_vectorstore(destino, embeddings=embeddings))
        existentes = almacen.get(include=["metadatas"])
        anteriores = {
            identificador: metadata["origen"]
            for identificador, metadata in zip(existentes["ids"], existentes["metadatas"])
        }
        actuales = {fragmento.id for fragmento in fragmentos}
        nuevos = [fragmento for fragmento in fragmentos if fragmento.id not in anteriores]
        obsoletos = sorted(anteriores.keys() - actuales)

        if nuevos and embeddings is None:
            almacen = recursos.enter_context(abrir_vectorstore(destino, embeddings=crear_embeddings()))
        for inicio in range(0, len(nuevos), 128):
            almacen.add_documents(nuevos[inicio:inicio + 128])
        for inicio in range(0, len(obsoletos), 128):
            almacen.delete(ids=obsoletos[inicio:inicio + 128])

    origenes = {documento.metadata["origen"] for documento in documentos}
    procesados = {fragmento.metadata["origen"] for fragmento in nuevos}
    procesados.update(anteriores[identificador] for identificador in obsoletos)
    return ResultadoIngesta(
        encontrados=len(documentos) + vacios,
        vacios=vacios,
        procesados=len(origenes & procesados),
        previamente_indexados=len(origenes - procesados),
        fragmentos_generados=len(fragmentos),
        fragmentos_nuevos=len(nuevos),
        fragmentos_eliminados=len(obsoletos),
        fragmentos_almacenados=len(actuales),
    )

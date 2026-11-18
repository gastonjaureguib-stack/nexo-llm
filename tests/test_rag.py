import json
import os
import tempfile
import unittest
from functools import partial
from pathlib import Path
from unittest.mock import AsyncMock, patch

import chromadb
import tiktoken
from chromadb.config import Settings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from nexo_rag.chain import crear_cadena, get_rag_response
from nexo_rag.config import CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION_NAME, EMBEDDING_MODEL, MIN_CHUNK_SIZE, TOP_K
from nexo_rag.ingestion import fragmentar_documentos, ingerir_documentos, leer_documentos
from nexo_rag.retriever import recuperar_documentos
from nexo_rag.schemas import RAGResponse
from nexo_rag.vectorstore import abrir_vectorstore


ENCODING = tiktoken.Encoding(
    name="test-bytes",
    pat_str=r"(?s).",
    mergeable_ranks={bytes([indice]): indice for indice in range(256)},
    special_tokens={},
)


def setUpModule():
    unittest.enterModuleContext(patch.dict(os.environ, {
        "LANGSMITH_TRACING": "false",
        "LANGSMITH_TRACING_V2": "false",
        "LANGCHAIN_TRACING": "false",
        "LANGCHAIN_TRACING_V2": "false",
    }))
    unittest.enterModuleContext(patch("tiktoken.get_encoding", return_value=ENCODING))


class EmbeddingsSimulados(Embeddings):
    def __init__(self):
        self.documentos = []
        self.consultas = []

    def vector(self, texto):
        texto = texto.lower()
        if any(termino in texto for termino in ("ssd", "disco", "volumen")):
            return [3.0, 0.0, 0.0]
        if any(termino in texto for termino in ("dns", "internet", "latencia")):
            return [0.0, 2.0, 0.0]
        return [0.0, 0.0, 1.0]

    def embed_documents(self, texts):
        self.documentos.extend(texts)
        return [self.vector(texto) for texto in texts]

    def embed_query(self, text):
        self.consultas.append(text)
        return self.vector(text)


class TestIngesta(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.datos = self.raiz / "data"
        self.datos.mkdir()
        self.destino = self.raiz / "vectorstore"
        self.embeddings = EmbeddingsSimulados()

    def escribir(self, archivo, texto):
        (self.datos / archivo).write_text(texto, encoding="utf-8")

    def ingerir(self):
        return ingerir_documentos(self.datos, self.destino, embeddings=self.embeddings)

    def test_lectura_extensiones_y_limpieza(self):
        self.escribir("RED.MD", "\ufeff  DNS resuelve nombres.\n")
        self.escribir("disco.txt", "SSD.")
        self.escribir("vacio.md", " \n\t")
        self.escribir("ignorar.csv", "DNS")
        (self.datos / "carpeta.md").mkdir()

        documentos, vacios = leer_documentos(self.datos)

        self.assertEqual(vacios, 1)
        self.assertCountEqual([doc.page_content for doc in documentos], ["DNS resuelve nombres.", "SSD."])
        red = next(doc for doc in documentos if doc.metadata["archivo"] == "RED.MD")
        self.assertEqual(red.metadata, {"archivo": "RED.MD", "origen": "RED.MD"})

    def test_ruta_inexistente_y_ruta_de_archivo(self):
        with self.assertRaises(FileNotFoundError):
            leer_documentos(self.datos / "no-existe")
        self.escribir("red.md", "DNS.")
        with self.assertRaises(NotADirectoryError):
            leer_documentos(self.datos / "red.md")

    def test_error_de_lectura_no_modifica_el_indice(self):
        self.escribir("anterior.md", "Mi volumen principal está lleno.")
        self.ingerir()
        (self.datos / "anterior.md").unlink()
        (self.datos / "invalido.md").write_bytes(b"\xff")

        with self.assertRaisesRegex(ValueError, "invalido.md"):
            self.ingerir()

        with abrir_vectorstore(self.destino) as almacen:
            registros = almacen.get(include=["metadatas"])
        self.assertEqual(registros["metadatas"][0]["origen"], "anterior.md")

    def test_fragmentacion_tokens_solapamiento_y_metadatos(self):
        texto = "".join(f"{indice:04d}" for indice in range(500))
        self.escribir("red.md", texto)
        documentos, _ = leer_documentos(self.datos)
        fragmentos = fragmentar_documentos(documentos)
        ids = [fragmento.id for fragmento in fragmentos]

        self.assertEqual(len(fragmentos), 3)
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(ids, [fragmento.id for fragmento in fragmentar_documentos(documentos)])
        self.assertEqual([len(ENCODING.encode(doc.page_content)) for doc in fragmentos], [800, 800, 500])
        for indice, fragmento in enumerate(fragmentos):
            self.assertEqual(fragmento.metadata, {
                "archivo": "red.md", "origen": "red.md", "indice": indice, "id": fragmento.id,
            })
        for anterior, siguiente in zip(fragmentos, fragmentos[1:]):
            self.assertEqual(
                ENCODING.encode(anterior.page_content)[-CHUNK_OVERLAP:],
                ENCODING.encode(siguiente.page_content)[:CHUNK_OVERLAP],
            )
        self.assertEqual(CHUNK_SIZE, 800)

    def test_fragmentacion_documento_corto_y_cola_sin_corte_valido(self):
        for longitud in (499, 500, 801, 949):
            with self.subTest(longitud=longitud):
                texto = "a" * longitud
                documento = Document(page_content=texto, metadata={"origen": "texto.md"})
                partes = fragmentar_documentos([documento])
                self.assertEqual([parte.page_content for parte in partes], [texto])

    def test_redistribuye_cola_sin_perder_texto_unicode(self):
        texto = ("Señal y latencia en el área de operación.\n\n" * 27).strip()
        documento = Document(page_content=texto, metadata={"origen": "red.md"})
        partes = [doc.page_content for doc in fragmentar_documentos([documento])]
        self.assertEqual(len(partes), 2)
        self.assertTrue(all(MIN_CHUNK_SIZE <= len(ENCODING.encode(parte)) <= CHUNK_SIZE for parte in partes))
        overlap = ENCODING.decode(ENCODING.encode(partes[1])[:CHUNK_OVERLAP])
        self.assertTrue(partes[0].endswith(overlap))
        self.assertEqual(partes[0] + partes[1][len(overlap):], texto)

    def test_persistencia_y_reingesta_sin_embeddings_nuevos(self):
        self.escribir("red.md", "Verificá primero DNS y latencia.")
        self.escribir("vacio.txt", " ")
        with patch("nexo_rag.ingestion.crear_embeddings", return_value=self.embeddings) as crear:
            inicial = ingerir_documentos(self.datos, self.destino)
        crear.assert_called_once_with()

        with abrir_vectorstore(self.destino, crear=False) as almacen:
            registros = almacen.get(include=["documents", "metadatas"])
        self.assertTrue((self.destino / "chroma.sqlite3").is_file())
        self.assertEqual(registros["documents"], ["Verificá primero DNS y latencia."])
        self.assertEqual(registros["ids"][0], registros["metadatas"][0]["id"])
        with patch("nexo_rag.ingestion.crear_embeddings") as crear:
            repetida = ingerir_documentos(self.datos, self.destino)

        crear.assert_not_called()
        self.assertEqual((inicial.encontrados, inicial.vacios, inicial.procesados), (2, 1, 1))
        self.assertEqual(inicial.fragmentos_nuevos, 1)
        self.assertEqual(repetida.previamente_indexados, 1)
        self.assertEqual(repetida.fragmentos_nuevos, 0)
        self.assertEqual(repetida.fragmentos_almacenados, 1)
        self.assertEqual(len(self.embeddings.documentos), 1)

    def test_actualiza_elimina_y_conserva_documentos(self):
        self.escribir("cambia.txt", "SSD original.")
        self.escribir("sale.md", "DNS obsoleto.")
        self.escribir("queda.md", "Registros.")
        self.ingerir()
        with abrir_vectorstore(self.destino) as almacen:
            anteriores = almacen.get(include=["metadatas"])
        ids = {
            metadata["origen"]: identificador
            for identificador, metadata in zip(anteriores["ids"], anteriores["metadatas"])
        }

        self.escribir("cambia.txt", "SSD actualizado.")
        self.escribir("nuevo.md", "Nuevo proceso de respaldo.")
        (self.datos / "sale.md").unlink()
        resultado = self.ingerir()

        with abrir_vectorstore(self.destino) as almacen:
            registros = almacen.get(include=["documents"])
        self.assertIn(ids["queda.md"], registros["ids"])
        self.assertNotIn(ids["cambia.txt"], registros["ids"])
        self.assertNotIn(ids["sale.md"], registros["ids"])
        self.assertCountEqual(registros["documents"], ["SSD actualizado.", "Nuevo proceso de respaldo.", "Registros."])
        self.assertEqual(self.embeddings.documentos[-2:], ["SSD actualizado.", "Nuevo proceso de respaldo."])
        self.assertEqual((resultado.procesados, resultado.previamente_indexados), (2, 1))
        self.assertEqual((resultado.fragmentos_nuevos, resultado.fragmentos_eliminados), (2, 2))

    def test_documento_vaciado_elimina_fragmentos(self):
        self.escribir("red.md", "Medición de latencia.")
        self.ingerir()
        self.escribir("red.md", "   ")

        resultado = self.ingerir()

        self.assertEqual((resultado.vacios, resultado.fragmentos_eliminados), (1, 1))
        self.assertEqual(resultado.fragmentos_almacenados, 0)

    def test_fallo_de_embedding_conserva_version_anterior(self):
        self.escribir("red.md", "DNS anterior.")
        self.ingerir()
        self.escribir("red.md", "DNS actualizado.")

        with patch.object(self.embeddings, "embed_documents", side_effect=ConnectionError):
            with self.assertRaises(ConnectionError):
                self.ingerir()

        with abrir_vectorstore(self.destino) as almacen:
            self.assertEqual(almacen.get(include=["documents"])["documents"], ["DNS anterior."])
        self.assertEqual(self.ingerir().fragmentos_eliminados, 1)

    def test_coleccion_incompatible_se_rechaza(self):
        for modelo, metrica in (("modelo-distinto", "cosine"), (EMBEDDING_MODEL, "l2")):
            with self.subTest(modelo=modelo, metrica=metrica):
                destino = self.raiz / metrica
                with chromadb.PersistentClient(
                    path=str(destino),
                    settings=Settings(
                        _env_file=None,
                        anonymized_telemetry=False,
                        chroma_otel_granularity="none",
                    ),
                ) as cliente:
                    cliente.create_collection(
                        COLLECTION_NAME, embedding_function=None,
                        metadata={"embedding_model": modelo},
                        configuration={"hnsw": {"space": metrica}},
                    )
                self.escribir("red.md", "DNS.")
                with self.assertRaisesRegex(ValueError, "métrica"):
                    ingerir_documentos(self.datos, destino, embeddings=self.embeddings)
        self.assertEqual(self.embeddings.documentos, [])


class TestRecuperacion(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.raiz = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.datos = self.raiz / "data"
        self.datos.mkdir()
        self.destino = self.raiz / "vectorstore"
        self.embeddings = EmbeddingsSimulados()

    async def test_recupera_por_similitud_y_limita_top_k(self):
        documentos = {
            "red.md": "DNS y latencia.",
            "disco.txt": "SSD con capacidad agotada.",
            "cpu.md": "Carga sostenida.",
            "memoria.md": "Paginación.",
            "cuentas.md": "Contraseñas.",
            "copias.md": "Restauración.",
        }
        for archivo, texto in documentos.items():
            (self.datos / archivo).write_text(texto, encoding="utf-8")
        ingerir_documentos(self.datos, self.destino, embeddings=self.embeddings)

        pregunta = "Internet va lento, ¿qué mido?"
        with patch("nexo_rag.retriever.crear_embeddings", return_value=self.embeddings) as crear:
            recuperados = await recuperar_documentos(pregunta, directorio=self.destino)

        crear.assert_called_once_with()
        self.assertEqual(len(recuperados), TOP_K)
        self.assertEqual(recuperados[0].metadata["origen"], "red.md")
        self.assertEqual(recuperados[0].page_content, documentos["red.md"])
        self.assertEqual(self.embeddings.consultas, [pregunta])
        self.assertEqual(len(self.embeddings.documentos), len(documentos))

    async def test_coleccion_ausente_o_vacia_no_genera_embedding(self):
        self.assertEqual(await recuperar_documentos("DNS", directorio=self.destino), [])
        self.assertFalse(self.destino.exists())
        self.destino.mkdir()
        self.assertEqual(await recuperar_documentos("DNS", directorio=self.destino), [])
        with abrir_vectorstore(self.destino):
            pass
        with patch("nexo_rag.retriever.crear_embeddings") as crear:
            self.assertEqual(await recuperar_documentos("DNS", directorio=self.destino), [])
        crear.assert_not_called()

    async def test_consulta_vacia(self):
        with self.assertRaises(ValueError):
            await recuperar_documentos("   ", directorio=self.destino)

    async def test_fallo_de_chroma_se_propaga(self):
        self.destino.mkdir()
        with patch("nexo_rag.retriever.abrir_vectorstore", side_effect=OSError("fallo local")):
            with self.assertRaisesRegex(OSError, "fallo local"):
                await recuperar_documentos("DNS", directorio=self.destino)

    async def test_ingesta_a_respuesta_con_chroma_real(self):
        (self.datos / "red.md").write_text("Revisá latencia y congestión.", encoding="utf-8")
        (self.datos / "disco.md").write_text("Revisá el espacio disponible en disco con df -h.", encoding="utf-8")
        ingerir_documentos(self.datos, self.destino, embeddings=self.embeddings)
        recuperar = partial(recuperar_documentos, directorio=self.destino, embeddings=self.embeddings)
        modelo = FakeListChatModel(responses=[
            '{"respuesta":"Revisá espacio con df -h.","referencias":["disco.md"]}',
            '{"respuesta":"No lo sé","referencias":[]}',
        ])
        cadena = crear_cadena(recuperar=recuperar, modelo=modelo)

        resultado = await cadena.ainvoke("¿Cómo compruebo cuánto espacio queda en el SSD?")
        self.assertEqual(resultado.referencias, ["disco.md"])
        self.assertIn("df -h", resultado.respuesta)
        resultado = await cadena.ainvoke("¿Cuál es la IP pública del servidor principal?")
        self.assertEqual(resultado.model_dump(), {"respuesta": "No lo sé", "referencias": []})
        self.assertEqual(len(self.embeddings.documentos), 2)
        self.assertEqual(len(self.embeddings.consultas), 2)


class TestRespuesta(unittest.TestCase):
    def test_validaciones(self):
        for respuesta, referencias in (
            (" ", []), ("Dato", [" "]), ("Dato", ["red.md", " red.md "]),
            ("Dato", []), ("No lo sé", ["red.md"]), ("Dato", [1]),
        ):
            with self.subTest(respuesta=respuesta, referencias=referencias):
                with self.assertRaises(ValidationError):
                    RAGResponse(respuesta=respuesta, referencias=referencias)

    def test_normalizacion(self):
        self.assertEqual(
            RAGResponse(respuesta=" Dato ", referencias=[" red.md "]).model_dump(),
            {"respuesta": "Dato", "referencias": ["red.md"]},
        )


class TestCadenaRAG(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.recuperar = AsyncMock(return_value=[
            Document(page_content="Revisá el volumen con df -h.", metadata={"origen": "storage.md"}),
        ])

    def mensaje(self, respuesta, referencias):
        return AIMessage(content=json.dumps({
            "respuesta": respuesta, "referencias": referencias,
        }, ensure_ascii=False))

    async def test_respuesta_y_contexto_con_referencias(self):
        with patch("nexo_rag.chain.crear_modelo") as crear:
            crear.return_value.ainvoke = AsyncMock(return_value=self.mensaje("Ejecutá df -h.", ["storage.md"]))
            cadena = crear_cadena(recuperar=self.recuperar)
            resultado = await cadena.ainvoke("  ¿Cómo reviso el disco?  ")

        self.assertEqual(resultado, RAGResponse(respuesta="Ejecutá df -h.", referencias=["storage.md"]))
        self.recuperar.assert_awaited_once_with("¿Cómo reviso el disco?")
        mensajes = crear.return_value.ainvoke.await_args.args[0].to_messages()
        self.assertIn("exclusivamente", mensajes[0].content)
        self.assertIn("referencias", mensajes[0].content)
        self.assertIn("¿Cómo reviso el disco?", mensajes[1].content)
        self.assertIn("storage.md", mensajes[1].content)
        self.assertIn("Revisá el volumen con df -h.", mensajes[1].content)

    async def test_preguntas_trampa_con_contexto(self):
        with patch("nexo_rag.chain.crear_modelo") as crear:
            crear.return_value.ainvoke = AsyncMock(return_value=self.mensaje("No lo sé", []))
            cadena = crear_cadena(recuperar=self.recuperar)
            for pregunta in (
                "¿Cuál es el salario mensual del director de Nexo Intelligence?",
                "¿Cuál es la dirección IP pública del servidor principal de Nexo Intelligence?",
            ):
                with self.subTest(pregunta=pregunta):
                    self.assertEqual(
                        (await cadena.ainvoke(pregunta)).model_dump(),
                        {"respuesta": "No lo sé", "referencias": []},
                    )
        self.assertEqual(self.recuperar.await_count, 2)

    async def test_sin_documentos_no_invoca_modelo(self):
        self.recuperar.return_value = []
        with patch("nexo_rag.chain.crear_modelo") as crear:
            resultado = await crear_cadena(recuperar=self.recuperar).ainvoke("DNS")
        crear.assert_not_called()
        self.assertEqual(resultado.model_dump(), {"respuesta": "No lo sé", "referencias": []})

    async def test_rechaza_referencias_inventadas_y_reintenta(self):
        with patch("nexo_rag.chain.crear_modelo") as crear:
            invocar = AsyncMock(return_value=self.mensaje("Dato", ["inventado.md"]))
            crear.return_value.ainvoke = invocar
            with self.assertRaises(OutputParserException):
                await crear_cadena(recuperar=self.recuperar).ainvoke("Disco")
        self.recuperar.assert_awaited_once()
        self.assertEqual(invocar.await_count, 3)

    async def test_recupera_tras_salida_invalida_y_truncada(self):
        with patch("nexo_rag.chain.crear_modelo") as crear:
            invocar = AsyncMock(side_effect=[
                AIMessage(content="{", response_metadata={"finish_reason": "length"}),
                self.mensaje("Dato sin referencias", []),
                self.mensaje("Ejecutá df -h.", ["storage.md"]),
            ])
            crear.return_value.ainvoke = invocar
            resultado = await crear_cadena(recuperar=self.recuperar).ainvoke("Disco")
        self.assertEqual(resultado.referencias, ["storage.md"])
        self.assertEqual(invocar.await_count, 3)
        self.recuperar.assert_awaited_once()

    async def test_error_de_proveedor_se_propaga_sin_reintentos(self):
        with patch("nexo_rag.chain.crear_modelo") as crear:
            invocar = AsyncMock(side_effect=ConnectionError("proveedor inaccesible"))
            crear.return_value.ainvoke = invocar
            with self.assertRaises(ConnectionError):
                await crear_cadena(recuperar=self.recuperar).ainvoke("Disco")
        invocar.assert_awaited_once()

    async def test_error_de_recuperacion_no_invoca_modelo(self):
        self.recuperar.side_effect = OSError("Chroma inaccesible")
        with patch("nexo_rag.chain.crear_modelo") as crear:
            with self.assertRaises(OSError):
                await crear_cadena(recuperar=self.recuperar).ainvoke("Disco")
        crear.assert_not_called()

    async def test_entrada_publica_rechaza_consulta_vacia(self):
        with patch("nexo_rag.chain.crear_modelo") as crear:
            with self.assertRaises(ValueError):
                await get_rag_response(" ")
        crear.assert_not_called()


if __name__ == "__main__":
    unittest.main()

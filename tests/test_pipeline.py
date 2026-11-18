
import json
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx2 import AsyncClient, MockTransport, Response
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from pydantic import ValidationError
from openai import LengthFinishReasonError
from openai.types.chat import ChatCompletion

from nexo_pipeline.chain import RespuestaTruncadaError, crear_cadena, process_text, prompt
from nexo_pipeline.schemas import ExtraccionTecnica, NivelCriticidad


def setUpModule():
    unittest.enterModuleContext(patch.dict(os.environ, {
        "LANGSMITH_TRACING": "false",
        "LANGSMITH_TRACING_V2": "false",
        "LANGCHAIN_TRACING": "false",
        "LANGCHAIN_TRACING_V2": "false",
    }))


class TestPipeline(unittest.IsolatedAsyncioTestCase):
    async def test_extraccion_asincrona(self):
        respuesta_simulada = """
        {
            "tecnologias": ["Node.js"],
            "nivel_de_criticidad": "alta",
            "resumen_tecnico": "El servidor dejó de responder."
        }
        """

        modelo_simulado = FakeListChatModel(
            responses=[respuesta_simulada]
        )

        parser = PydanticOutputParser(
            pydantic_object=ExtraccionTecnica
        )

        cadena = prompt | modelo_simulado | parser

        resultado = await cadena.ainvoke(
            {
                "texto": (
                    "El servidor Node.js dejó de responder "
                    "y los usuarios no pueden acceder."
                )
            }
        )

        self.assertIsInstance(resultado, ExtraccionTecnica)
        self.assertEqual(resultado.tecnologias, ["Node.js"])
        self.assertEqual(
            resultado.nivel_de_criticidad,
            NivelCriticidad.ALTA
        )
        self.assertEqual(
            resultado.resumen_tecnico,
            "El servidor dejó de responder."
        )

    async def test_json_malformado(self):
        respuesta_simulada = """
        {
            "tecnologias": ["Node.js"],
            "nivel_de_criticidad": "alta",
            "resumen_tecnico":
        """

        modelo_simulado = FakeListChatModel(
            responses=[respuesta_simulada]
        )

        parser = PydanticOutputParser(
            pydantic_object=ExtraccionTecnica
        )

        cadena = prompt | modelo_simulado | parser

        with self.assertRaises(OutputParserException):
            await cadena.ainvoke(
                {"texto": "El servidor Node.js dejó de responder."}
            )


class TestEsquemaExtraccion(unittest.TestCase):
    def test_validacion(self):
        valido = {
            "tecnologias": ["Node.js"],
            "nivel_de_criticidad": "alta",
            "resumen_tecnico": "Servicio interrumpido",
        }
        for campo, valores in {
            "tecnologias": [[], [" "], [1], "Node.js"],
            "nivel_de_criticidad": ["urgente", "ALTA", None],
            "resumen_tecnico": ["", "  ", None],
        }.items():
            for valor in valores:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValidationError):
                    ExtraccionTecnica.model_validate({**valido, campo: valor})
        for campo in valido:
            with self.subTest(faltante=campo), self.assertRaises(ValidationError):
                ExtraccionTecnica.model_validate({k: v for k, v in valido.items() if k != campo})
        for nivel in NivelCriticidad:
            self.assertEqual(ExtraccionTecnica(**{**valido, "nivel_de_criticidad": nivel}).nivel_de_criticidad, nivel)


class TestCadenaProduccion(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.datos = {
            "tecnologias": ["Node.js"],
            "nivel_de_criticidad": "alta",
            "resumen_tecnico": "Servicio interrumpido",
        }

    def respuesta(self, *, parsed=None, error=None, finish_reason="stop"):
        return {
            "raw": AIMessage(content="", response_metadata={"finish_reason": finish_reason}),
            "parsed": parsed,
            "parsing_error": error,
        }

    def cadena(self, respuestas):
        invocar = AsyncMock(side_effect=respuestas)
        async def generar(entrada):
            return await invocar(entrada)
        modelo = MagicMock()
        modelo.with_structured_output.return_value = RunnableLambda(generar)
        cadena = crear_cadena(modelo)
        modelo.with_structured_output.assert_called_once_with(ExtraccionTecnica, include_raw=True)
        return cadena, invocar

    async def test_process_text_valido(self):
        cadena, invocar = self.cadena([self.respuesta(parsed=self.datos)])
        with patch("nexo_pipeline.chain.crear_cadena", return_value=cadena), self.assertLogs("nexo_pipeline.chain", level="INFO") as logs:
            resultado = await process_text("Node.js no responde")
        self.assertEqual(resultado, ExtraccionTecnica(**self.datos))
        invocar.assert_awaited_once()
        mensajes = " ".join(logs.output)
        self.assertIn("Inicio", mensajes)
        self.assertIn("validada", mensajes)

    async def test_reintento_parseo(self):
        cadena, invocar = self.cadena([
            self.respuesta(error=OutputParserException("JSON inválido")),
            self.respuesta(parsed=self.datos),
        ])
        with self.assertLogs("nexo_pipeline.chain", level="WARNING") as logs:
            resultado = await cadena.ainvoke({"texto": "Node.js"})
        self.assertEqual(resultado.tecnologias, ["Node.js"])
        self.assertEqual(invocar.await_count, 2)
        self.assertIn("Reintento", " ".join(logs.output))

    async def test_reintento_validacion(self):
        cadena, invocar = self.cadena([
            self.respuesta(parsed={**self.datos, "tecnologias": []}),
            self.respuesta(parsed=self.datos),
        ])
        await cadena.ainvoke({"texto": "Node.js"})
        self.assertEqual(invocar.await_count, 2)

    async def test_reintentos_agotados(self):
        cadena, invocar = self.cadena([self.respuesta(error=OutputParserException("JSON inválido"))] * 3)
        with patch("nexo_pipeline.chain.crear_cadena", return_value=cadena), self.assertLogs("nexo_pipeline.chain", level="WARNING") as logs:
            with self.assertRaises(OutputParserException):
                await process_text("Node.js")
        self.assertEqual(invocar.await_count, 3)
        self.assertEqual(sum("Reintento" in log for log in logs.output), 2)
        self.assertIn("Fallo definitivo", " ".join(logs.output))

    async def test_truncamiento_aun_con_datos_validos(self):
        cadena, invocar = self.cadena([self.respuesta(parsed=self.datos, finish_reason="length")] * 3)
        with self.assertRaises(RespuestaTruncadaError):
            await cadena.ainvoke({"texto": "Node.js"})
        self.assertEqual(invocar.await_count, 3)

    async def test_truncamiento_recuperable(self):
        cadena, invocar = self.cadena([
            self.respuesta(finish_reason="length", error=OutputParserException("incompleto")),
            self.respuesta(parsed=self.datos),
        ])
        resultado = await cadena.ainvoke({"texto": "Node.js"})
        self.assertEqual(resultado.tecnologias, ["Node.js"])
        self.assertEqual(invocar.await_count, 2)

    async def test_truncamiento_reportado_por_sdk(self):
        completion = ChatCompletion(
            id="test", created=0, model="test-model", object="chat.completion",
            choices=[{"finish_reason": "length", "index": 0,
                      "message": {"role": "assistant", "content": "{"}}],
        )
        cadena, invocar = self.cadena([
            LengthFinishReasonError(completion=completion),
            self.respuesta(parsed=self.datos),
        ])
        resultado = await cadena.ainvoke({"texto": "Node.js"})
        self.assertEqual(resultado.tecnologias, ["Node.js"])
        self.assertEqual(invocar.await_count, 2)

    async def test_respuesta_ausente(self):
        cadena, invocar = self.cadena([self.respuesta()] * 3)
        with self.assertRaises(OutputParserException):
            await cadena.ainvoke({"texto": "Node.js"})
        self.assertEqual(invocar.await_count, 3)

    async def test_error_no_recuperable(self):
        cadena, invocar = self.cadena([RuntimeError("configuración inválida")])
        with self.assertRaises(RuntimeError):
            await cadena.ainvoke({"texto": "Node.js"})
        invocar.assert_awaited_once()

    async def test_texto_vacio(self):
        with patch("nexo_pipeline.chain.crear_cadena") as crear:
            for texto in ("", "  ", None):
                with self.subTest(texto=texto), self.assertRaises(ValueError):
                    await process_text(texto)
            crear.assert_not_called()

    async def test_integracion_parser_chatopenai_sin_red(self):
        respuestas = iter([("length", "{"), ("stop", json.dumps(self.datos))])
        solicitudes = []

        def responder(request):
            solicitudes.append(json.loads(request.content))
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url.path, "/v1/chat/completions")
            finish_reason, content = next(respuestas)
            return Response(200, json={
                "id": "chatcmpl-test",
                "created": 0,
                "model": "gpt-4o-mini",
                "object": "chat.completion",
                "choices": [{
                    "index": 0,
                    "finish_reason": finish_reason,
                    "message": {"role": "assistant", "content": content},
                }],
            })

        async with AsyncClient(transport=MockTransport(responder)) as cliente:
            modelo = ChatOpenAI(
                model="gpt-4o-mini",
                api_key="test-only",
                base_url="https://openai.invalid/v1",
                max_retries=0,
                http_async_client=cliente,
            )
            resultado = await crear_cadena(modelo).ainvoke({"texto": "Node.js"})

        self.assertEqual(resultado, ExtraccionTecnica(**self.datos))
        self.assertEqual(len(solicitudes), 2)
        for solicitud in solicitudes:
            self.assertEqual(solicitud["response_format"]["type"], "json_schema")
            self.assertEqual(solicitud["messages"][-1]["content"], "Node.js")


if __name__ == "__main__":
    unittest.main()

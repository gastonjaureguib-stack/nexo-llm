
import logging
import os

from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from openai import LengthFinishReasonError
from pydantic import ValidationError

from nexo_pipeline.schemas import ExtraccionTecnica


logger = logging.getLogger(__name__)


class RespuestaTruncadaError(OutputParserException):
    pass


class _RegistroReintentos(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, *, tags=None, name=None, **kwargs):
        if name == "extraer":
            for tag in tags or []:
                if tag.startswith("retry:attempt:"):
                    logger.warning("Reintento de extracción: intento %s", tag.rsplit(":", 1)[1])


INSTRUCCIONES_EXTRACCION = """
            Sos un analista especializado en sistemas informáticos.

            Tu tarea es analizar textos técnicos y extraer:
            - Las tecnologías mencionadas explícitamente.
            - El nivel de criticidad: baja, media o alta.
            - Un resumen técnico breve y preciso.

            Criterios de criticidad:
            - Baja: información general, operaciones normales o avisos menores.
            - Media: errores parciales, degradación del servicio o problemas recuperables.
            - Alta: interrupciones del servicio, pérdida de datos o fallos críticos.

            No inventes tecnologías que no aparezcan en el texto.
            La extracción requiere al menos una tecnología explícita.
            Si no hay ninguna, no inventes nombres: la respuesta no será válida.
            Basá la criticidad exclusivamente en la información disponible.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", "{instrucciones}"), ("human", "{texto}")]
).partial(instrucciones=INSTRUCCIONES_EXTRACCION)


def _validar_respuesta(respuesta):
    raw = respuesta["raw"]
    if raw.response_metadata.get("finish_reason") == "length":
        raise RespuestaTruncadaError("Respuesta truncada por límite de tokens")
    if respuesta["parsing_error"] is not None:
        raise respuesta["parsing_error"]
    if respuesta["parsed"] is None:
        raise OutputParserException("El modelo no devolvió una extracción")
    resultado = ExtraccionTecnica.model_validate(respuesta["parsed"])
    logger.info("Respuesta validada correctamente")
    return resultado


def crear_cadena(modelo=None):
    if modelo is None:
        load_dotenv()
        modelo = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini",
            temperature=0,
            max_tokens=1000,
            max_retries=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    cadena = prompt | modelo.with_structured_output(ExtraccionTecnica, include_raw=True)

    async def extraer(entrada):
        try:
            return _validar_respuesta(await cadena.ainvoke(entrada))
        except Exception as error:
            logger.warning("Error de extracción: %s", type(error).__name__)
            raise

    return RunnableLambda(extraer, name="extraer").with_retry(
        retry_if_exception_type=(OutputParserException, ValidationError, LengthFinishReasonError),
        stop_after_attempt=3,
        wait_exponential_jitter=False,
    ).with_config(callbacks=[_RegistroReintentos()])


async def process_text(text: str) -> ExtraccionTecnica:
    logger.info("Inicio del procesamiento")
    try:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("El texto técnico no puede estar vacío")
        return await crear_cadena().ainvoke({"texto": text})
    except Exception as error:
        logger.error("Fallo definitivo de extracción: %s", type(error).__name__)
        raise

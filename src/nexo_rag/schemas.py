from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SIN_INFORMACION = "No lo sé"


class RAGResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    respuesta: str = Field(min_length=1)
    referencias: list[str]

    @field_validator("respuesta")
    @classmethod
    def validar_respuesta(cls, respuesta: str) -> str:
        respuesta = respuesta.strip()
        if not respuesta:
            raise ValueError("La respuesta no puede estar vacía.")
        return respuesta

    @field_validator("referencias")
    @classmethod
    def validar_referencias(cls, referencias: list[str]) -> list[str]:
        referencias = [referencia.strip() for referencia in referencias]
        if any(not referencia for referencia in referencias):
            raise ValueError("Las referencias no pueden estar vacías.")
        if len(referencias) != len(set(referencias)):
            raise ValueError("Las referencias no pueden estar duplicadas.")
        return referencias

    @model_validator(mode="after")
    def validar_evidencia(self) -> Self:
        requiere_referencias = self.respuesta != SIN_INFORMACION
        if bool(self.referencias) != requiere_referencias:
            raise ValueError("Solo las respuestas con información deben incluir referencias.")
        return self

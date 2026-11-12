from enum import Enum

from pydantic import BaseModel, Field, field_validator


class NivelCriticidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class ExtraccionTecnica(BaseModel):
    tecnologias: list[str] = Field(
        min_length=1,
        description="Tecnologías identificadas en el texto"
    )
    nivel_de_criticidad: NivelCriticidad
    resumen_tecnico: str = Field(min_length=1)

    @field_validator("tecnologias")
    @classmethod
    def validar_tecnologias(cls, tecnologias: list[str]) -> list[str]:
        if any(not tecnologia.strip() for tecnologia in tecnologias):
            raise ValueError("Las tecnologías no pueden contener nombres vacíos")
        return tecnologias

    @field_validator("resumen_tecnico")
    @classmethod
    def validar_resumen(cls, resumen: str) -> str:
        if not resumen.strip():
            raise ValueError("El resumen técnico no puede estar vacío")
        return resumen

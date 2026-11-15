from typing import Literal

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=10000,
        description="Pregunta o instrucción del usuario.",
    )

    thread_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        description="Identificador de conversación para recuperar su memoria.",
    )

    mode: Literal["auto", "research", "analysis"] = Field(
        default="auto",
        description="Modo de ejecución solicitado.",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("La pregunta no puede estar vacía.")

        return value

    @field_validator("thread_id")
    @classmethod
    def validate_thread_id(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("El thread_id no puede estar vacío.")

        return value

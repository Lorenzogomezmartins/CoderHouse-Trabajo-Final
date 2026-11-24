from typing import Any, Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class RetrievedDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")

    document_id: str = Field(min_length=1)
    content: str = ""
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("document_id")
    @classmethod
    def validate_document_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El ID del documento no puede estar vacío.")
        return value


class AgentMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El contenido del mensaje no puede estar vacío.")
        return value


class AnalysisMetrics(BaseModel):
    documents_analyzed: int = Field(ge=0)
    local_documents_analyzed: int = Field(ge=0)
    benefit_documents: int = Field(ge=0)
    risk_documents: int = Field(ge=0)
    coverage_percentage: float = Field(ge=0, le=100)


class ResearchAgentOutput(BaseModel):
    context: str = ""
    sources: list[RetrievedDocument] = Field(default_factory=list)
    agent: Literal["research"] = "research"
    answer: str | None = None
    messages: list[AgentMessage] | None = None


class AnalystAgentOutput(BaseModel):
    answer: str = Field(min_length=1)
    agent: Literal["analyst"] = "analyst"
    messages: list[AgentMessage]
    analysis_metrics: AnalysisMetrics

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("La respuesta del analista no puede estar vacía.")
        return value

import pytest
from pydantic import ValidationError

from app.schemas.agent_outputs import (
    RetrievedDocument,
    ResearchAgentOutput,
    AnalystAgentOutput,
)


def test_retrieved_document_accepts_valid_data():
    document = RetrievedDocument(
        document_id="python-001",
        content="Python es un lenguaje de programación.",
        score=0.95,
        metadata={"source": "python.md"},
    )

    assert document.document_id == "python-001"
    assert document.score == 0.95


def test_retrieved_document_rejects_blank_id():
    with pytest.raises(ValidationError):
        RetrievedDocument(document_id="   ")


def test_research_output_rejects_invalid_agent():
    with pytest.raises(ValidationError):
        ResearchAgentOutput(agent="analyst")


def test_analyst_output_accepts_valid_data():
    output = AnalystAgentOutput(
        answer="Análisis completado.",
        agent="analyst",
        messages=[
            {"role": "assistant", "content": "Análisis completado."}
        ],
        analysis_metrics={
            "documents_analyzed": 5,
            "local_documents_analyzed": 3,
            "benefit_documents": 2,
            "risk_documents": 1,
            "coverage_percentage": 60,
        },
    )

    assert output.agent == "analyst"
    assert output.analysis_metrics.coverage_percentage == 60


def test_analyst_output_rejects_invalid_coverage():
    with pytest.raises(ValidationError):
        AnalystAgentOutput(
            answer="Análisis completado.",
            messages=[
                {"role": "assistant", "content": "Análisis completado."}
            ],
            analysis_metrics={
                "documents_analyzed": 5,
                "local_documents_analyzed": 3,
                "benefit_documents": 2,
                "risk_documents": 1,
                "coverage_percentage": 150,
            },
        )


def test_analyst_output_rejects_blank_answer():
    with pytest.raises(ValidationError):
        AnalystAgentOutput(
            answer="   ",
            messages=[
                {"role": "assistant", "content": "Respuesta"}
            ],
            analysis_metrics={
                "documents_analyzed": 0,
                "local_documents_analyzed": 0,
                "benefit_documents": 0,
                "risk_documents": 0,
                "coverage_percentage": 0,
            },
        )

import pytest
from pydantic import ValidationError

from app.schemas.requests import QueryRequest


def test_query_request_valid():
    request = QueryRequest(
        question="¿Qué es Python?",
        mode="research",
        thread_id="test-001",
    )
    assert request.question == "¿Qué es Python?"
    assert request.mode == "research"


def test_query_request_rejects_short_question():
    with pytest.raises(ValidationError):
        QueryRequest(question="Hi")


def test_query_request_rejects_invalid_mode():
    with pytest.raises(ValidationError):
        QueryRequest(question="Pregunta válida", mode="invalid")


def test_query_request_strips_whitespace():
    request = QueryRequest(question="  ¿Qué es Python?  ")
    assert request.question == "¿Qué es Python?"

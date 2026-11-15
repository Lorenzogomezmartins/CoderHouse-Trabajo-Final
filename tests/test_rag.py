import pytest

from app.agents.research_agent import research_agent


@pytest.mark.asyncio
async def test_research_retrieves_documents_and_generates_answer(monkeypatch):
    async def fake_retrieve(question, top_k=5):
        assert question == "¿Qué es Python?"
        assert top_k == 5

        return [
            {
                "document_id": "python-001",
                "content": "Python es un lenguaje de programación.",
                "score": 0.95,
                "metadata": {"source": "python.md"},
            }
        ]

    async def fake_generate(prompt):
        assert "Python es un lenguaje de programación." in prompt
        return "Python es un lenguaje de programación interpretado."

    monkeypatch.setattr(
        "app.agents.research_agent.retrieve_documents",
        fake_retrieve,
    )
    monkeypatch.setattr(
        "app.agents.research_agent.generate_text",
        fake_generate,
    )

    result = await research_agent({
        "question": "¿Qué es Python?",
        "mode": "research",
        "messages": [],
    })

    assert result["agent"] == "research"
    assert len(result["sources"]) == 1
    assert "Python" in result["answer"]
    assert len(result["messages"]) == 2


@pytest.mark.asyncio
async def test_research_preserves_previous_messages(monkeypatch):
    async def fake_retrieve(question, top_k=5):
        return []

    async def fake_generate(prompt):
        assert "Mi lenguaje favorito es Python" in prompt
        return "Tu lenguaje favorito es Python."

    monkeypatch.setattr(
        "app.agents.research_agent.retrieve_documents",
        fake_retrieve,
    )
    monkeypatch.setattr(
        "app.agents.research_agent.generate_text",
        fake_generate,
    )

    result = await research_agent({
        "question": "¿Cuál es mi lenguaje favorito?",
        "mode": "research",
        "messages": [
            {
                "role": "user",
                "content": "Mi lenguaje favorito es Python",
            }
        ],
    })

    assert result["messages"][0]["content"] == "Mi lenguaje favorito es Python"
    assert "Python" in result["answer"]

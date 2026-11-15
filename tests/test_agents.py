import pytest

from app.agents.supervisor import supervisor_agent
from app.agents.analyst_agent import analyst_agent


@pytest.mark.asyncio
async def test_supervisor_selects_research():
    result = await supervisor_agent({
        "question": "Buscá información",
        "mode": "research",
    })
    assert result["next_step"] == "research"


@pytest.mark.asyncio
async def test_supervisor_selects_analyst():
    result = await supervisor_agent({
        "question": "Analizá esta información",
        "mode": "analysis",
    })
    assert result["next_step"] == "analyst"


@pytest.mark.asyncio
async def test_analyst_uses_conversation_history(monkeypatch):
    captured = {}

    async def fake_generate_text(prompt):
        captured["prompt"] = prompt
        return "Tu lenguaje favorito es Python."

    monkeypatch.setattr(
        "app.agents.analyst_agent.generate_text",
        fake_generate_text,
    )

    result = await analyst_agent({
        "question": "¿Cuál es mi lenguaje favorito?",
        "context": "",
        "messages": [
            {"role": "user", "content": "Mi lenguaje favorito es Python."},
            {"role": "assistant", "content": "Lo tendré en cuenta."},
        ],
    })

    assert "Python" in captured["prompt"]
    assert result["answer"] == "Tu lenguaje favorito es Python."
    assert len(result["messages"]) == 4

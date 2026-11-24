from app.state import AgentState
from app.services.llm import generate_text

from app.schemas.agent_outputs import (
    AnalystAgentOutput,
    AnalysisMetrics,
)


def calculate_analysis_metrics(
    documents: list[dict],
) -> dict:
    local_docs = [
        doc for doc in documents
        if (doc.get("metadata") or {}).get("origin")
        == "pre-entrega-6"
    ]

    risks = sum(
        1 for doc in local_docs
        if "riesgo" in (
            (doc.get("metadata") or {}).get("title", "")
            + doc.get("content", "")
        ).lower()
    )

    benefits = sum(
        1 for doc in local_docs
        if any(
            word in (
                (doc.get("metadata") or {}).get("title", "")
                + doc.get("content", "")
            ).lower()
            for word in (
                "beneficio",
                "productividad",
                "automatización",
            )
        )
    )

    return AnalysisMetrics(
        documents_analyzed=len(documents),
        local_documents_analyzed=len(local_docs),
        benefit_documents=benefits,
        risk_documents=risks,
        coverage_percentage=round(
            len(local_docs) / 5 * 100,
            2,
        ),
    ).model_dump()


async def analyst_agent(state: AgentState) -> dict:
    question = state["question"]
    context = state.get("context", "")
    previous_messages = state.get("messages", [])
    documents = state.get("sources", [])

    metrics = calculate_analysis_metrics(documents)

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in previous_messages[-10:]
    )

    prompt = f"""
Sos un asistente técnico especializado en programación e ingeniería de software.
Respondé en español claro, preciso y directo.
Tené en cuenta el historial disponible.
Utilizá los documentos recuperados cuando sean relevantes.
No inventes información. Si el contexto no alcanza, aclaralo.

HISTORIAL:
{history_text or "Es el comienzo de la conversación."}

CONTEXTO RECUPERADO:
{context or "No se recuperaron documentos relevantes."}

MÉTRICAS DE INVESTIGACIÓN:
{metrics}

PREGUNTA:
{question}

Redactá una respuesta útil y estructurada.
"""

    answer = await generate_text(prompt)

    updated_messages = previous_messages + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]

    output = AnalystAgentOutput(
        answer=answer,
        agent="analyst",
        messages=updated_messages[-20:],
        analysis_metrics=metrics,
    )

    return output.model_dump()
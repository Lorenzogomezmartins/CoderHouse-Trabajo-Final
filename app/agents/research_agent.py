import asyncio

from app.state import AgentState
from app.rag.retriever import retrieve_documents
from app.rag.local_retriever import search_knowledge_base
from app.services.llm import generate_text
from app.schemas.agent_outputs import ResearchAgentOutput


async def research_agent(state: AgentState) -> dict:
    question = state["question"]
    previous_messages = state.get("messages", [])

    pinecone_docs, local_docs = await asyncio.gather(
        retrieve_documents(question, top_k=5),
        asyncio.to_thread(
            search_knowledge_base,
            question,
            5,
        ),
    )

    documents = pinecone_docs + local_docs

    context = "\n\n".join(
        f"Fuente: "
        f"{doc.get('metadata', {}).get('title') or doc.get('metadata', {}).get('source', doc['document_id'])}\n"
        f"{doc.get('content', '')}"
        for doc in documents
        if doc.get("content")
    )

    if state.get("mode") == "research":
        history_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in previous_messages[-10:]
        )

        prompt = f"""
Sos un asistente técnico especializado en programación e ingeniería de software.
Respondé en español claro, preciso y directo.
Tené en cuenta el historial de conversación.
Usá los documentos recuperados como fuente complementaria.
No inventes información ni atribuyas a los documentos datos que no contienen.

HISTORIAL:
{history_text or "Es el comienzo de la conversación."}

DOCUMENTOS RECUPERADOS:
{context or "No se recuperaron documentos relevantes."}

PREGUNTA:
{question}

Respondé directamente.
"""

        answer = await generate_text(prompt)

        updated_messages = previous_messages + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]

        output = ResearchAgentOutput(
            context=context,
            sources=documents,
            answer=answer,
            agent="research",
            messages=updated_messages[-20:],
        )

        return output.model_dump(exclude_none=True)

    output = ResearchAgentOutput(
        context=context,
        sources=documents,
        agent="research",
    )

    return output.model_dump(exclude_none=True)
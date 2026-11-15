import pytest
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class MemoryState(TypedDict, total=False):
    question: str
    messages: list[dict[str, str]]
    answer: str


async def memory_node(state: MemoryState) -> dict:
    previous = state.get("messages", [])
    question = state.get("question", "")

    updated = previous + [
        {"role": "user", "content": question}
    ]

    return {
        "messages": updated,
        "answer": f"Mensajes recuperados: {len(updated)}",
    }


def create_memory_graph(checkpointer):
    builder = StateGraph(MemoryState)

    builder.add_node("memory", memory_node)
    builder.add_edge(START, "memory")
    builder.add_edge("memory", END)

    return builder.compile(checkpointer=checkpointer)


@pytest.mark.asyncio
async def test_sqlite_memory_persists_between_invocations(tmp_path):
    database = str(tmp_path / "test_memory.db")

    async with AsyncSqliteSaver.from_conn_string(database) as checkpointer:
        await checkpointer.setup()
        graph = create_memory_graph(checkpointer)

        config = {
            "configurable": {
                "thread_id": "persistent-test-001"
            }
        }

        first = await graph.ainvoke(
            {"question": "Mi lenguaje favorito es Python"},
            config=config,
        )

        second = await graph.ainvoke(
            {"question": "¿Cuál es mi lenguaje favorito?"},
            config=config,
        )

        assert len(first["messages"]) == 1
        assert len(second["messages"]) == 2

        assert (
            second["messages"][0]["content"]
            == "Mi lenguaje favorito es Python"
        )


@pytest.mark.asyncio
async def test_sqlite_separates_conversation_threads(tmp_path):
    database = str(tmp_path / "separate_threads.db")

    async with AsyncSqliteSaver.from_conn_string(database) as checkpointer:
        await checkpointer.setup()
        graph = create_memory_graph(checkpointer)

        await graph.ainvoke(
            {"question": "Dato de conversación A"},
            config={
                "configurable": {"thread_id": "thread-A"}
            },
        )

        second = await graph.ainvoke(
            {"question": "Pregunta de conversación B"},
            config={
                "configurable": {"thread_id": "thread-B"}
            },
        )

        assert len(second["messages"]) == 1

        assert (
            second["messages"][0]["content"]
            == "Pregunta de conversación B"
        )

from pathlib import Path
from contextlib import asynccontextmanager
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.types import Command

from app.config import settings
from app.graph import build_graph
from app.memory.checkpointer import get_checkpointer
from app.schemas.requests import QueryRequest
from app.schemas.responses import QueryResponse, HealthResponse
from app.services.llm import LLMUnavailableError
from app.observability import (
    configure_observability,
    build_traced_executor,
)


class ApprovalRequest(BaseModel):
    approved: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_observability()

    async with get_checkpointer() as checkpointer:
        app.state.graph = build_graph(checkpointer)
        app.state.execute_graph = build_traced_executor(
            app.state.graph
        )
        yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Sistema multiagente con RAG híbrido, "
        "HITL, memoria persistente y Gemini."
    ),
    version="1.2.0",
    lifespan=lifespan,
)


def get_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id
        }
    }


async def get_task_snapshot(thread_id: str):
    snapshot = await app.state.graph.aget_state(
        get_config(thread_id)
    )

    if not snapshot.values:
        raise HTTPException(
            status_code=404,
            detail="No existe esa tarea.",
        )

    return snapshot


def serialize_task(thread_id: str, snapshot) -> dict:
    values = snapshot.values or {}
    interrupts = []

    for task in snapshot.tasks:
        for interruption in getattr(task, "interrupts", ()):
            interrupts.append(
                getattr(interruption, "value", str(interruption))
            )

    if interrupts:
        status = "WAITING_APPROVAL"
    elif snapshot.next:
        status = "RUNNING"
    else:
        status = "COMPLETED"

    return {
        "thread_id": thread_id,
        "status": status,
        "question": values.get("question"),
        "answer": values.get("answer"),
        "agent": values.get("agent"),
        "approved": values.get("approved"),
        "approval_message": values.get("approval_message"),
        "approval_request": interrupts,
        "sources": values.get("sources", []),
        "analysis_metrics": values.get("analysis_metrics", {}),
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        application=settings.app_name,
        version="1.2.0",
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    thread_id = request.thread_id or str(uuid4())
    config = get_config(thread_id)

    try:
        result = await app.state.execute_graph(
            {
                "question": request.question,
                "mode": request.mode,
                "thread_id": thread_id,
                "context": "",
                "sources": [],
            },
            config,
        )

        if result.get("__interrupt__"):
            raise HTTPException(
                status_code=409,
                detail=(
                    "La tarea requiere aprobación humana. "
                    f"Usá POST /tasks. Thread: {thread_id}"
                ),
            )

        return QueryResponse(
            answer=result.get("answer", result.get("context", "")),
            thread_id=thread_id,
            agent=result.get("agent", "unknown"),
            sources=result.get("sources", []),
            analysis_metrics=result.get("analysis_metrics", {}),
        )

    except HTTPException:
        raise
    except LLMUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "Error ejecutando el sistema IA: "
                f"{type(error).__name__}: {error}"
            ),
        )


@app.post("/tasks", status_code=202)
async def create_task(request: QueryRequest):
    thread_id = request.thread_id or str(uuid4())
    config = get_config(thread_id)

    try:
        await app.state.execute_graph(
            {
                "question": request.question,
                "mode": request.mode,
                "thread_id": thread_id,
                "context": "",
                "sources": [],
            },
            config,
        )

        snapshot = await get_task_snapshot(thread_id)
        return serialize_task(thread_id, snapshot)

    except LLMUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Error procesando la tarea: {type(error).__name__}: {error}",
        )


@app.get("/tasks/{thread_id}")
async def task_status(thread_id: str):
    snapshot = await get_task_snapshot(thread_id)
    return serialize_task(thread_id, snapshot)


@app.post("/tasks/{thread_id}/approve")
async def approve_task(
    thread_id: str,
    request: ApprovalRequest,
):
    config = get_config(thread_id)
    snapshot = await get_task_snapshot(thread_id)

    waiting = any(
        getattr(task, "interrupts", ())
        for task in snapshot.tasks
    )

    if not waiting:
        raise HTTPException(
            status_code=409,
            detail="La tarea no está esperando aprobación.",
        )

    try:
        await app.state.execute_graph(
            Command(resume={"approved": request.approved}),
            config,
        )

        updated_snapshot = await get_task_snapshot(thread_id)
        return serialize_task(thread_id, updated_snapshot)

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Error reanudando la tarea: {type(error).__name__}: {error}",
        )
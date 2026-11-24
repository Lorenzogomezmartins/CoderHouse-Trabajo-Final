import logging
import os
from typing import Any, Callable

from langsmith import traceable

from app.config import settings

logger = logging.getLogger(__name__)


def configure_observability() -> bool:
    os.environ["LANGSMITH_TRACING"] = str(
        settings.langsmith_tracing
    ).lower()

    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint

    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key

    if settings.langsmith_tracing and not settings.langsmith_api_key:
        logger.warning(
            "LangSmith está habilitado, pero falta LANGSMITH_API_KEY."
        )
        return False

    if settings.langsmith_tracing:
        logger.info(
            "LangSmith habilitado. Proyecto: %s",
            settings.langsmith_project,
        )
        return True

    logger.info("Trazabilidad LangSmith deshabilitada.")
    return False


def build_traced_executor(graph: Any) -> Callable:
    @traceable(
        name="langgraph_execution",
        run_type="chain",
    )
    async def execute_graph(
        inputs: Any,
        config: dict,
    ) -> dict:
        return await graph.ainvoke(
            inputs,
            config=config,
        )

    return execute_graph
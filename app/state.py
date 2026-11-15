from typing import Any, TypedDict

class AgentState(TypedDict, total=False):
    question: str
    mode: str
    thread_id: str
    next_step: str
    context: str
    answer: str
    agent: str
    sources: list[dict[str, Any]]
    messages: list[dict[str, str]]
    error: str
    requires_approval: bool
    approved: bool
    approval_message: str
    analysis_metrics: dict[str, Any]

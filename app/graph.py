from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.agents.supervisor import supervisor_agent
from app.agents.research_agent import research_agent
from app.agents.analyst_agent import analyst_agent
from app.agents.hitl import approval_node

def route_after_approval(state: AgentState) -> str:
    if state.get("requires_approval") and not state.get("approved"):
        return "rejected"
    return state.get("next_step", "research")

def route_after_research(state: AgentState) -> str:
    if state.get("mode") == "research":
        return "finish"
    return "analyst"

def rejected_node(state: AgentState) -> dict:
    return {
        "answer": "La tarea fue rechazada. No se ejecutó el procesamiento solicitado.",
        "agent": "approval",
    }

def build_graph(checkpointer):
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_agent)
    builder.add_node("approval", approval_node)
    builder.add_node("research", research_agent)
    builder.add_node("analyst", analyst_agent)
    builder.add_node("rejected", rejected_node)

    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "approval")

    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "research": "research",
            "analyst": "analyst",
            "rejected": "rejected",
        },
    )

    builder.add_conditional_edges(
        "research",
        route_after_research,
        {
            "analyst": "analyst",
            "finish": END,
        },
    )

    builder.add_edge("analyst", END)
    builder.add_edge("rejected", END)

    return builder.compile(checkpointer=checkpointer)

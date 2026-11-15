from app.state import AgentState
from app.agents.hitl import is_critical_query

async def supervisor_agent(state: AgentState) -> dict:
    mode = state.get("mode", "auto")
    destination = "analyst" if mode == "analysis" else "research"
    critical = is_critical_query(state.get("question", ""))

    return {
        "next_step": destination,
        "agent": "supervisor",
        "requires_approval": critical,
        "approved": not critical,
    }

import unicodedata
from langgraph.types import interrupt

CRITICAL_KEYWORDS = (
    "elimin", "borr", "public", "envi",
    "compr", "pag", "transfer", "produccion",
    "modificar datos", "ejecutar comando",
)

def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )

def is_critical_query(query: str) -> bool:
    normalized = normalize_text(query)
    return any(word in normalized for word in CRITICAL_KEYWORDS)

def approval_node(state: dict) -> dict:
    if not state.get("requires_approval", False):
        return {"approved": True}

    decision = interrupt({
        "type": "human_approval",
        "message": "Esta tarea requiere aprobación humana.",
        "query": state.get("question", ""),
    })

    approved = (
        decision.get("approved", False)
        if isinstance(decision, dict)
        else bool(decision)
    )

    return {
        "approved": approved,
        "approval_message": (
            "Tarea aprobada por un usuario."
            if approved else "Tarea rechazada por un usuario."
        ),
    }

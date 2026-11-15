import json
import re
from pathlib import Path

STOP_WORDS = {
    "para", "como", "sobre", "entre", "desde", "hasta",
    "este", "esta", "estos", "estas", "tema", "analizar",
    "analiza", "investiga", "informacion", "disponible",
    "una", "uno", "unos", "unas", "con", "por", "del",
    "las", "los", "que", "empresa", "inteligencia"
}

def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-záéíóúñü]+", text.lower())
    return {
        word for word in words
        if len(word) > 3 and word not in STOP_WORDS
    }

def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    path = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json"

    with path.open("r", encoding="utf-8-sig") as file:
        documents = json.load(file)

    query_terms = tokenize(query)
    if not query_terms:
        return []

    results = []
    for document in documents:
        content = (
            document["tema"] + " " +
            document["titulo"] + " " +
            document["contenido"]
        )
        matches = query_terms.intersection(tokenize(content))
        if matches:
            results.append({
                "document_id": f"local-{document['id']}",
                "content": document["contenido"],
                "score": float(len(matches)),
                "metadata": {
                    "source": document["fuente"],
                    "title": document["titulo"],
                    "topic": document["tema"],
                    "matched_terms": sorted(matches),
                    "origin": "pre-entrega-6"
                }
            })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )[:limit]

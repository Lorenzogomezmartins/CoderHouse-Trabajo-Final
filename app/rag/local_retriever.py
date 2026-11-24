import json
import re
from pathlib import Path

from pydantic import BaseModel, Field

from app.schemas.agent_outputs import RetrievedDocument


STOP_WORDS = {
    "para", "como", "sobre", "entre", "desde", "hasta",
    "este", "esta", "estos", "estas", "tema", "analizar",
    "analiza", "investiga", "informacion", "disponible",
    "una", "uno", "unos", "unas", "con", "por", "del",
    "las", "los", "que", "empresa", "inteligencia"
}


class LocalRetrievalRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10000)
    limit: int = Field(default=5, ge=1, le=20)


def tokenize(text: str) -> set[str]:
    words = re.findall(
        r"[a-záéíóúñü]+",
        text.lower(),
    )

    return {
        word for word in words
        if len(word) > 3 and word not in STOP_WORDS
    }


def search_knowledge_base(
    query: str,
    limit: int = 5,
) -> list[dict]:
    request = LocalRetrievalRequest(
        query=query,
        limit=limit,
    )

    path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "knowledge_base.json"
    )

    with path.open("r", encoding="utf-8-sig") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError(
            "La base de conocimiento debe ser una lista."
        )

    query_terms = tokenize(request.query)

    if not query_terms:
        return []

    results = []

    for document in documents:
        content = (
            document["tema"] + " "
            + document["titulo"] + " "
            + document["contenido"]
        )

        matches = query_terms.intersection(
            tokenize(content)
        )

        if matches:
            validated = RetrievedDocument.model_validate({
                "document_id": f"local-{document['id']}",
                "content": document["contenido"],
                "score": float(len(matches)),
                "metadata": {
                    "source": document["fuente"],
                    "title": document["titulo"],
                    "topic": document["tema"],
                    "matched_terms": sorted(matches),
                    "origin": "pre-entrega-6",
                },
            })

            results.append(validated.model_dump())

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )[:request.limit]
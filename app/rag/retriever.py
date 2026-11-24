from pydantic import BaseModel, Field

from pinecone import PineconeAsyncio

from app.config import settings
from app.rag.embeddings import embed_text
from app.schemas.agent_outputs import RetrievedDocument


class RetrievalRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    top_k: int = Field(default=5, ge=1, le=20)


async def retrieve_documents(
    question: str,
    top_k: int = 5,
) -> list[dict]:
    request = RetrievalRequest(
        question=question,
        top_k=top_k,
    )

    vector = await embed_text(
        request.question,
        "RETRIEVAL_QUERY",
    )

    async with PineconeAsyncio(
        api_key=settings.pinecone_api_key
    ) as pc:
        index = await pc.index(
            name=settings.pinecone_index_name
        )

        async with index:
            result = await index.query(
                vector=vector,
                top_k=request.top_k,
                namespace=settings.pinecone_namespace,
                include_metadata=True,
            )

    documents = []

    for match in result.matches:
        document = RetrievedDocument.model_validate({
            "document_id": match.id,
            "content": (match.metadata or {}).get("text", ""),
            "score": (
                float(match.score)
                if match.score is not None
                else None
            ),
            "metadata": match.metadata or {},
        })

        documents.append(document.model_dump())

    return documents
from pinecone import PineconeAsyncio

from app.config import settings
from app.rag.embeddings import embed_text


async def retrieve_documents(question: str, top_k: int = 5) -> list[dict]:
    vector = await embed_text(question, "RETRIEVAL_QUERY")

    async with PineconeAsyncio(api_key=settings.pinecone_api_key) as pc:
        index = await pc.index(name=settings.pinecone_index_name)

        async with index:
            result = await index.query(
                vector=vector,
                top_k=top_k,
                namespace=settings.pinecone_namespace,
                include_metadata=True,
            )

    return [
        {
            "document_id": match.id,
            "content": (match.metadata or {}).get("text", ""),
            "score": float(match.score) if match.score is not None else None,
            "metadata": match.metadata or {},
        }
        for match in result.matches
    ]

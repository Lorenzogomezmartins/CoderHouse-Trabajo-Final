import asyncio
import hashlib
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from pinecone import AsyncPinecone

from app.config import settings
from app.rag.embeddings import embed_text


DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def split_text(text: str) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


async def main():
    files = [
        path for path in DOCUMENTS_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    ]

    if not files:
        print("No hay documentos TXT o MD en data/documents.")
        return

    vectors = []

    for file in files:
        print("Procesando:", file.name)
        text = file.read_text(encoding="utf-8")
        chunks = split_text(text)

        for position, chunk in enumerate(chunks):
            vector = await embed_text(chunk, "RETRIEVAL_DOCUMENT")

            identifier = hashlib.sha256(
                f"{file.relative_to(DOCUMENTS_DIR)}:{position}".encode("utf-8")
            ).hexdigest()

            vectors.append({
                "id": identifier,
                "values": vector,
                "metadata": {
                    "text": chunk,
                    "source": file.name,
                    "chunk": position,
                },
            })

    async with AsyncPinecone(
        api_key=settings.pinecone_api_key
    ) as pc:
        index = await pc.index(name=settings.pinecone_index_name)

        async with index:
            result = await index.upsert(
                vectors=vectors,
                batch_size=50,
            )

    print("\nINGESTA COMPLETADA")
    print("ARCHIVOS:", len(files))
    print("VECTORES:", len(vectors))
    print("RESULTADO:", result)


if __name__ == "__main__":
    asyncio.run(main())

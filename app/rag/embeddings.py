import math
from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings


@lru_cache
def get_genai_client():
    if not settings.google_api_key:
        raise ValueError("Falta GOOGLE_API_KEY en .env")

    return genai.Client(api_key=settings.google_api_key)


async def embed_text(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    if not text or not text.strip():
        raise ValueError("No se puede generar un embedding vacío.")

    client = get_genai_client()

    response = await client.aio.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=settings.embedding_dimension,
        ),
    )

    if not response.embeddings:
        raise RuntimeError("Google no devolvió embeddings.")

    values = response.embeddings[0].values

    if len(values) != settings.embedding_dimension:
        raise ValueError(
            f"Dimensión incorrecta: {len(values)}. "
            f"Esperada: {settings.embedding_dimension}"
        )

    # Gemini Embedding 001 requiere normalización al reducir dimensiones.
    norm = math.sqrt(sum(value * value for value in values))

    if norm == 0:
        raise ValueError("El embedding generado tiene norma cero.")

    return [float(value / norm) for value in values]

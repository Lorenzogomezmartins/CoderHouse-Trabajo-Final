import asyncio
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


class LLMUnavailableError(RuntimeError):
    pass


@lru_cache
def get_chat_model() -> ChatGoogleGenerativeAI:
    if not settings.google_api_key:
        raise ValueError("Falta GOOGLE_API_KEY en .env")

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
        max_retries=0,
    )


def extract_text(content) -> str:
    """Extrae texto limpio de las distintas estructuras de respuesta."""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") == "text" and block.get("text"):
                    text_parts.append(str(block["text"]))

        return "\n".join(part.strip() for part in text_parts if part.strip())

    if isinstance(content, dict):
        if content.get("type") == "text" and content.get("text"):
            return str(content["text"]).strip()

    return str(content).strip()


async def generate_text(prompt: str) -> str:
    if not prompt or not prompt.strip():
        raise ValueError("El prompt no puede estar vacío.")

    model = get_chat_model()

    try:
        response = await asyncio.wait_for(
            model.ainvoke(prompt),
            timeout=35,
        )
    except asyncio.TimeoutError as error:
        raise LLMUnavailableError(
            "Gemini superó el tiempo máximo de espera de 35 segundos."
        ) from error
    except Exception as error:
        message = str(error)

        if any(code in message for code in (
            "503",
            "UNAVAILABLE",
            "429",
            "RESOURCE_EXHAUSTED",
        )):
            raise LLMUnavailableError(
                f"Gemini no está disponible temporalmente: {message}"
            ) from error

        raise

    return extract_text(response.content)

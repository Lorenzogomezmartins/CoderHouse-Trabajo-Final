import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config import settings
from google import genai


async def main():
    print("Consultando modelos de Google...")

    client = genai.Client(api_key=settings.google_api_key)

    try:
        models = await client.aio.models.list()

        print("\nMODELOS DE EMBEDDINGS DISPONIBLES:")

        async for model in models:
            name = getattr(model, "name", "") or ""

            if "embedding" in name.lower():
                print("-", name)

    except Exception as error:
        print("ERROR CONSULTANDO MODELOS:", type(error).__name__)
        print(error)

    finally:
        await client.aio.aclose()


if __name__ == "__main__":
    asyncio.run(main())

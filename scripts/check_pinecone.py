import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config import get_settings
from pinecone import PineconeAsyncio


async def main():
    settings = get_settings()
    print("INDICE CONFIGURADO:", settings.pinecone_index_name)

    async with PineconeAsyncio(
        api_key=settings.pinecone_api_key
    ) as pc:
        description = await pc.describe_index(
            settings.pinecone_index_name
        )

        print("\nPINECONE CONECTADO")
        print("NOMBRE:", description.name)
        print("DIMENSION:", description.dimension)
        print("METRICA:", description.metric)
        print("HOST:", description.host)
        print("ESTADO:", description.status)


if __name__ == "__main__":
    asyncio.run(main())

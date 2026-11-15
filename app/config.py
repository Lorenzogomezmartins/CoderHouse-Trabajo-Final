from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "The Intelligence System"
    app_env: str = "development"
    debug: bool = True

    google_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768

    pinecone_api_key: str = ""
    pinecone_index_name: str = ""
    pinecone_namespace: str = "docs-tecnicas"

    database_path: str = str(BASE_DIR / "data" / "memory.db")

    phoenix_collector_endpoint: str = "http://localhost:6006"
    phoenix_project_name: str = "the-intelligence-system"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

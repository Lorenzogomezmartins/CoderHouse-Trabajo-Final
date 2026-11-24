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
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768

    pinecone_api_key: str = ""
    pinecone_index_name: str = ""
    pinecone_namespace: str = "docs-tecnicas"

    database_path: str = str(BASE_DIR / "data" / "memory.db")

    langsmith_tracing: bool = True
    langsmith_api_key: str = ""
    langsmith_project: str = "the-intelligence-system"
    langsmith_endpoint: str = "https://api.smith.langchain.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
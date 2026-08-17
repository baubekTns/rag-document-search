"""Typed application settings loaded from environment variables."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


def _cors_origins(value: str) -> tuple[str, ...]:
    origins = tuple(origin.strip() for origin in value.split(",") if origin.strip())
    return origins or ("http://localhost:5173",)


@dataclass(frozen=True)
class Settings:
    sqlite_database_path: Path
    upload_directory: Path
    upload_staging_directory: Path
    max_upload_size_bytes: int
    upload_stream_chunk_size: int
    ingestion_concurrency: int
    embedding_concurrency: int
    cors_origins: tuple[str, ...]
    qdrant_url: str
    qdrant_collection_name: str
    qdrant_timeout_seconds: float
    embedding_model_name: str
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_seconds: float
    ollama_max_output_tokens: int
    ollama_max_retries: int
    readiness_timeout_seconds: float


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    upload_directory = Path(os.getenv("UPLOAD_DIRECTORY", "uploads"))
    return Settings(
        sqlite_database_path=Path(os.getenv("SQLITE_DATABASE_PATH", "data/documents.db")),
        upload_directory=upload_directory,
        upload_staging_directory=Path(
            os.getenv("UPLOAD_STAGING_DIRECTORY", str(upload_directory / ".staging"))
        ),
        max_upload_size_bytes=int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(10 * 1024 * 1024))),
        upload_stream_chunk_size=int(os.getenv("UPLOAD_STREAM_CHUNK_SIZE", str(64 * 1024))),
        ingestion_concurrency=int(os.getenv("INGESTION_CONCURRENCY", "2")),
        embedding_concurrency=int(os.getenv("EMBEDDING_CONCURRENCY", "1")),
        cors_origins=_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:5173")),
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        qdrant_collection_name=os.getenv("QDRANT_COLLECTION_NAME", "document_chunks"),
        qdrant_timeout_seconds=float(os.getenv("QDRANT_TIMEOUT_SECONDS", "10")),
        embedding_model_name=os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        ollama_timeout_seconds=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120")),
        ollama_max_output_tokens=int(os.getenv("OLLAMA_MAX_OUTPUT_TOKENS", "512")),
        ollama_max_retries=int(os.getenv("OLLAMA_MAX_RETRIES", "1")),
        readiness_timeout_seconds=float(os.getenv("READINESS_TIMEOUT_SECONDS", "2")),
    )

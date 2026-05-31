from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    whisper_model: str = "small"
    database_url: str = "postgresql://youtube:youtube@localhost:5432/youtube_rag"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    enable_audio_fallback: bool = True
    audio_download_dir: str = ".cache/audio"
    chunk_size: int = 1200
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        if value < 200:
            raise ValueError("CHUNK_SIZE must be at least 200.")
        return value

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int, info) -> int:
        if value < 0:
            raise ValueError("CHUNK_OVERLAP must be non-negative.")
        chunk_size = info.data.get("chunk_size")
        if isinstance(chunk_size, int) and value >= chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE.")
        return value

    @property
    def pgvector_connection_url(self) -> str:
        if self.database_url.startswith("postgresql+"):
            return self.database_url
        if self.database_url.startswith("postgres://"):
            return "postgresql+psycopg://" + self.database_url.removeprefix("postgres://")
        if self.database_url.startswith("postgresql://"):
            return "postgresql+psycopg://" + self.database_url.removeprefix("postgresql://")
        return self.database_url

    @property
    def psycopg_connection_url(self) -> str:
        if self.database_url.startswith("postgresql+psycopg://"):
            return "postgresql://" + self.database_url.removeprefix("postgresql+psycopg://")
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()

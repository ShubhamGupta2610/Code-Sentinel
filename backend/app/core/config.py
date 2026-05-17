"""Application configuration using Pydantic settings."""
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # GitHub
    GITHUB_APP_ID: str = "test-app-id"
    GITHUB_PRIVATE_KEY: str = "test-key"
    GITHUB_WEBHOOK_SECRET: str = "devsecret"

    # Infrastructure
    DATABASE_URL: str = "sqlite:///./codesentinel.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "codellama"
    OPENAI_API_KEY: str | None = None

    # Limits
    MAX_DIFF_LINES: int = 150
    MAX_COMMENTS_PER_PR: int = 10
    CONFIDENCE_THRESHOLD: float = 0.85
    LOG_LEVEL: str = "DEBUG"

    # Frontend
    REACT_APP_API_URL: str = "http://localhost:8000"

    # GitHub status context
    STATUS_CONTEXT: str = "CodeSentinel/review"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

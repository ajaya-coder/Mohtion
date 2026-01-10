"""Application configuration via environment variables."""

import base64
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitHub App
    github_app_id: str
    github_private_key_base64: str  # Base64 encoded PEM
    github_webhook_secret: str

    # LLM
    anthropic_api_key: str

    # Redis (for ARQ job queue)
    redis_url: str = "redis://localhost:6379"

    # Database
    database_url: str = "postgresql+asyncpg://mohtion:password@localhost:5432/mohtion"

    # App settings
    debug: bool = False
    log_level: str = "INFO"

    # Agent settings
    max_retries: int = 2
    max_prs_per_day: int = 3
    default_complexity_threshold: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def github_private_key(self) -> str:
        """Decode the base64 encoded private key."""
        return base64.b64decode(self.github_private_key_base64).decode("utf-8")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

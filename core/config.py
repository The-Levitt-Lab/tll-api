from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment.

    Defaults are safe for local development. Override via environment variables.
    """

    APP_NAME: str = "Vittcoin API"
    ENV: str = "development"
    DEBUG: bool = True

    # Async DB URL (SQLite by default). Example for Postgres:
    # postgresql+asyncpg://user:pass@localhost:5432/dbname
    DATABASE_URL: str = "sqlite+aiosqlite:///./data.db"

    # Comma-separated CORS origins
    ALLOWED_ORIGINS: str = ""

    # API version prefix
    API_V1_PREFIX: str = "/api/v1"

    # Dev convenience to auto-create tables at startup
    AUTO_CREATE_TABLES: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def allowed_origins_list(self) -> List[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
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

    # Security
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # OAuth Client IDs
    GOOGLE_CLIENT_ID: str = ""
    APPLE_CLIENT_ID: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        if not v:
            return "sqlite+aiosqlite:///./data.db"
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # asyncpg uses 'ssl' param, not 'sslmode'
        if "sslmode=require" in v:
            v = v.replace("sslmode=require", "ssl=require")
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.development"),
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


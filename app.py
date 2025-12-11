from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.v1 import api_router
from core.config import get_settings
from core.logging import configure_logging
from db.base import Base
import db.models
from db.session import engine


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    if settings.AUTO_CREATE_TABLES:
        # Development convenience: ensure tables exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    # CORS
    allowed_origins = settings.allowed_origins_list()
    if allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"name": settings.APP_NAME, "status": "ok"}

    return app


app = create_app()

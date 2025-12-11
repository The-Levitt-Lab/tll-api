from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import get_settings


settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


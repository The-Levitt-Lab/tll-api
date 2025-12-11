from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from schemas import UserCreate


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def list_users(
    session: AsyncSession, *, offset: int = 0, limit: int = 100
) -> List[User]:
    result = await session.execute(select(User).offset(offset).limit(limit))
    return list(result.scalars().all())


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    user = User(email=str(user_in.email), full_name=user_in.full_name)
    session.add(user)
    await session.flush()
    await session.refresh(user)
    await session.commit()
    return user

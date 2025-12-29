from __future__ import annotations

import re
import secrets
from typing import List, Optional, Any

from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Transaction
from schemas import UserCreate


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def list_users(
    session: AsyncSession, *, offset: int = 0, limit: int = 100
) -> List[User]:
    result = await session.execute(select(User).offset(offset).limit(limit))
    return list(result.scalars().all())


async def get_users_with_cumulative_earnings(
    session: AsyncSession, *, offset: int = 0, limit: int = 100
) -> List[Any]:
    stmt = (
        select(
            User.id, 
            User.username, 
            User.full_name, 
            func.coalesce(func.sum(Transaction.amount), 0).label("cumulative_earned")
        )
        .outerjoin(Transaction, (Transaction.user_id == User.id) & (Transaction.amount > 0))
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(Transaction.amount), 0).desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.all()


def _generate_base_username(full_name: str) -> str:
    """Generate a base username from full name (e.g., 'John Smith' -> '@john.smith')."""
    normalized = re.sub(r"\s+", ".", full_name.strip()).lower()
    # Remove any characters that aren't alphanumeric or dots
    normalized = re.sub(r"[^a-z0-9.]", "", normalized)
    return f"@{normalized}" if normalized else "@user"


async def _generate_unique_username(session: AsyncSession, full_name: str) -> str:
    """Generate a unique username, appending a random suffix if needed."""
    base_username = _generate_base_username(full_name)
    
    # Try the base username first
    existing = await get_user_by_username(session, base_username)
    if not existing:
        return base_username
    
    # Base username taken - append a random 4-character suffix
    # This is more robust than incrementing numbers (avoids race conditions)
    for _ in range(10):  # Try up to 10 times
        suffix = secrets.token_hex(2)  # 4 hex characters
        candidate = f"{base_username}.{suffix}"
        existing = await get_user_by_username(session, candidate)
        if not existing:
            return candidate
    
    # Fallback: use a longer random suffix (extremely unlikely to reach here)
    return f"{base_username}.{secrets.token_hex(4)}"


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    full_name = user_in.full_name or ""
    username = await _generate_unique_username(session, full_name)
    
    user = User(email=str(user_in.email), full_name=full_name, username=username)
    session.add(user)
    
    try:
        await session.flush()
    except IntegrityError as e:
        await session.rollback()
        # Check if it's a username collision (could happen in race condition)
        if "username" in str(e).lower():
            # Retry with a new random username
            username = f"@{secrets.token_hex(4)}"
            user = User(email=str(user_in.email), full_name=full_name, username=username)
            session.add(user)
            await session.flush()
        else:
            # It's likely an email collision - let caller handle it
            raise
    
    await session.refresh(user)
    await session.commit()
    return user


async def update_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

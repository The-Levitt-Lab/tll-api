from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import create_user, get_user_by_email, get_user_by_id, list_users
from schemas import UserCreate


class AlreadyExistsError(Exception):
    pass


class NotFoundError(Exception):
    pass


async def create_user_service(session: AsyncSession, user_in: UserCreate):
    existing = await get_user_by_email(session, str(user_in.email))
    if existing is not None:
        raise AlreadyExistsError("User with this email already exists")
    return await create_user(session, user_in)


async def list_users_service(
    session: AsyncSession, *, offset: int = 0, limit: int = 100
):
    return await list_users(session, offset=offset, limit=limit)


async def get_user_service(session: AsyncSession, user_id: int):
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AlreadyExistsError, NotFoundError
from repositories import (
    create_transaction,
    create_user,
    get_user_by_email,
    get_user_by_id,
    list_users,
    update_user,
    get_users_with_cumulative_earnings,
)
from schemas import UserCreate
from schemas.transaction import TransactionCreate


async def create_user_service(session: AsyncSession, user_in: UserCreate):
    existing = await get_user_by_email(session, str(user_in.email))
    if existing is not None:
        raise AlreadyExistsError("User with this email already exists")
    
    # Create user
    user = await create_user(session, user_in)
    
    # Record initial balance transaction
    if user.balance > 0:
        await create_transaction(session, TransactionCreate(
            user_id=user.id,
            amount=user.balance,
            type="credit",
            description="Welcome Bonus"
        ))
    
    return user


async def list_users_service(
    session: AsyncSession, *, offset: int = 0, limit: int = 100
):
    return await list_users(session, offset=offset, limit=limit)


async def get_user_service(session: AsyncSession, user_id: int):
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


async def update_user_balance_service(
    session: AsyncSession, 
    user_id: int, 
    amount: int,
    description: str | None = None,
    admin_id: int | None = None
):
    user = await get_user_service(session, user_id)
    user.balance += amount
    await update_user(session, user)
    
    # Create transaction record
    tx_type = "credit" if amount > 0 else "debit"
    if description is None:
        description = "Admin adjustment"
        
    await create_transaction(session, TransactionCreate(
        user_id=user_id,
        amount=amount,
        type=tx_type,
        description=description,
        admin_id=admin_id
    ))
    
    return user


async def get_leaderboard_service(
    session: AsyncSession, *, offset: int = 0, limit: int = 100
):
    return await get_users_with_cumulative_earnings(session, offset=offset, limit=limit)

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_admin
from db.models import User
from db.session import get_db_session
from repositories import get_transactions_by_user_id, get_requests_by_user_id
from schemas import UserRead, RequestRead, LeaderboardEntry
from schemas.transaction import TransactionRead
from services import (
    NotFoundError,
    get_user_service,
    list_users_service,
    get_leaderboard_service,
)
from utils import PaginationParams


router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(
    p: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(require_admin),
):
    """List all users (admin only)."""
    users = await list_users_service(db, offset=p.offset, limit=p.limit)
    return users


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    p: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    """Get the leaderboard (requires authentication)."""
    return await get_leaderboard_service(db, offset=p.offset, limit=p.limit)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


@router.get("/me/transactions", response_model=list[TransactionRead])
async def get_my_transactions(
    p: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the current user's transactions."""
    transactions = await get_transactions_by_user_id(
        db, current_user.id, offset=p.offset, limit=p.limit
    )
    return transactions


@router.get("/me/requests", response_model=list[RequestRead])
async def get_my_requests(
    p: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the current user's payment requests."""
    requests = await get_requests_by_user_id(
        db, current_user.id, offset=p.offset, limit=p.limit
    )
    return requests


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    """Get a user by ID (requires authentication)."""
    try:
        return await get_user_service(db, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

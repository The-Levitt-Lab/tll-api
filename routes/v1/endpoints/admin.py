from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import require_admin
from db.session import get_db_session
from db.models import User
from schemas import UserRead
from schemas.user import UserBalanceUpdate
from services import NotFoundError
from services.user_service import update_user_balance_service, get_user_service

router = APIRouter()


@router.post("/users/{user_id}/balance/add", response_model=UserRead)
async def add_balance(
    user_id: int,
    data: UserBalanceUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Add to a user's balance. Requires admin role."""
    try:
        user = await update_user_balance_service(db, user_id, data.amount)
        return user
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/users/{user_id}/balance/subtract", response_model=UserRead)
async def subtract_balance(
    user_id: int,
    data: UserBalanceUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Subtract from a user's balance. Requires admin role."""
    try:
        user = await update_user_balance_service(db, user_id, -data.amount)
        return user
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


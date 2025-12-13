from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import require_admin
from db.session import get_db_session
from db.models import User
from repositories import get_all_transactions
from schemas import UserBalanceUpdate, UserRead
from schemas.transaction import TransactionRead
from services import NotFoundError
from services.user_service import update_user_balance_service, get_user_service
from utils import PaginationParams

router = APIRouter()


@router.get("/transactions", response_model=list[TransactionRead])
async def list_all_transactions(
    p: PaginationParams = Depends(),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """List all transactions. Requires admin role."""
    transactions = await get_all_transactions(db, offset=p.offset, limit=p.limit)
    return transactions



@router.post("/users/{user_id}/balance/add", response_model=UserRead)
async def add_balance(
    user_id: int,
    data: UserBalanceUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Add to a user's balance. Requires admin role."""
    try:
        user = await update_user_balance_service(
            db, 
            user_id, 
            data.amount, 
            description="Admin added balance",
            admin_id=admin.id
        )
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
        user = await update_user_balance_service(
            db, 
            user_id, 
            -data.amount, 
            description="Admin subtracted balance",
            admin_id=admin.id
        )
        return user
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

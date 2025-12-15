from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from db.models import User
from db.session import get_db_session
from repositories import get_transactions_by_user_id, get_requests_by_user_id
from schemas import UserCreate, UserRead, RequestRead
from schemas.transaction import TransactionRead
from services import (
    AlreadyExistsError,
    NotFoundError,
    get_user_service,
    list_users_service,
    create_user_service,
)
from utils import PaginationParams


router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(
    p: PaginationParams = Depends(), db: AsyncSession = Depends(get_db_session)
):
    users = await list_users_service(db, offset=p.offset, limit=p.limit)
    return users


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    try:
        user = await create_user_service(db, user_in)
        return user
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/transactions", response_model=list[TransactionRead])
async def get_my_transactions(
    p: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
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
    requests = await get_requests_by_user_id(
        db, current_user.id, offset=p.offset, limit=p.limit
    )
    return requests


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        return await get_user_service(db, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

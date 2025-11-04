from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import get_db_session
from api.schemas import UserCreate, UserRead
from api.services import (
    AlreadyExistsError,
    NotFoundError,
    get_user_service,
    list_users_service,
    create_user_service,
)
from api.utils import PaginationParams


router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(p: PaginationParams = Depends(), db: AsyncSession = Depends(get_db_session)):
    users = await list_users_service(db, offset=p.offset, limit=p.limit)
    return users


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    try:
        user = await create_user_service(db, user_in)
        return user
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        return await get_user_service(db, user_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


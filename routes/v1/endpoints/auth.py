"""Authentication endpoints using Clerk."""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AlreadyExistsError
from core.security import create_access_token
from db.session import get_db_session
from repositories.user_repository import get_user_by_email
from schemas.auth import LoginRequest, Token
from schemas.user import UserCreate
from services.auth_service import get_clerk_user_info
from services.user_service import create_user_service

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db_session)) -> Any:
    """
    Authenticate a user with a Clerk session token.
    
    1. Verifies the Clerk token and extracts user info
    2. Creates a new user if they don't exist
    3. Returns an internal access token for API authentication
    """
    # 1. Verify Clerk token and get user info
    user_info = await get_clerk_user_info(data.token)
    
    email = user_info["email"]
    # Prefer passed full_name, then token full_name, then fallback to email prefix
    full_name = data.full_name or user_info.get("full_name") or email.split("@")[0]
    
    # 2. Check if user exists
    user = await get_user_by_email(db, email)
    if not user:
        # 3. Create user if not exists
        try:
            user_in = UserCreate(email=email, full_name=full_name)
            user = await create_user_service(db, user_in)
        except (IntegrityError, AlreadyExistsError):
            # Race condition: another request created this user simultaneously
            # Rollback the failed transaction and fetch the existing user
            await db.rollback()
            user = await get_user_by_email(db, email)
            if not user:
                # This shouldn't happen, but handle it gracefully
                raise
    
    # 4. Create internal access token
    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }

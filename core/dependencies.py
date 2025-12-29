"""Authentication dependencies for FastAPI routes."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from db.session import get_db_session
from db.models import User
from repositories import get_user_by_id, get_user_by_email, get_user_by_clerk_id
from services.auth_service import verify_clerk_token

settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Extract and validate authentication token, return the current user.
    
    Supports two authentication methods:
    1. Internal JWT tokens (issued by /auth/login after Clerk verification)
    2. Direct Clerk session tokens (verified against Clerk's JWKS)
    
    The token type is auto-detected based on the algorithm in the header.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Peek at the token header to determine the type
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "")
        
        if algorithm == "RS256":
            # This is a Clerk token (RSA signed)
            user = await _authenticate_with_clerk_token(token, db, credentials_exception)
        else:
            # This is an internal token (HS256 signed)
            user = await _authenticate_with_internal_token(token, db, credentials_exception)
        
        return user
        
    except jwt.PyJWTError:
        raise credentials_exception


async def _authenticate_with_internal_token(
    token: str,
    db: AsyncSession,
    credentials_exception: HTTPException,
) -> User:
    """Validate an internal JWT token issued by our API."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    return user


async def _authenticate_with_clerk_token(
    token: str,
    db: AsyncSession,
    credentials_exception: HTTPException,
) -> User:
    """Validate a Clerk session token and find/create the user."""
    try:
        claims = await verify_clerk_token(token)
    except HTTPException:
        raise credentials_exception
    
    # Extract user identifiers from Clerk claims
    clerk_user_id = claims.get("sub")
    email = claims.get("email") or claims.get("primary_email_address")
    
    # Try to find user by clerk_user_id first (more reliable)
    user = None
    if clerk_user_id:
        user = await get_user_by_clerk_id(db, clerk_user_id)
    
    # Fallback to email lookup for backwards compatibility
    if user is None and email:
        user = await get_user_by_email(db, email)
    
    if user is None:
        # User doesn't exist yet - they need to call /auth/login first
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not registered. Please call /auth/login first.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require the current user to have admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

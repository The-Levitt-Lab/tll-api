"""Authentication schemas for Clerk-based auth."""
from pydantic import BaseModel

from schemas.user import UserRead


class LoginRequest(BaseModel):
    """Request body for login endpoint.
    
    The token should be a Clerk session token obtained from the frontend.
    Optionally include full_name for new user registration.
    """
    token: str
    full_name: str | None = None


class Token(BaseModel):
    """Response for successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserRead

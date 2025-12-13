from enum import Enum

from pydantic import BaseModel


class AuthProvider(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"
    DEV = "dev"


class LoginRequest(BaseModel):
    token: str
    provider: AuthProvider
    full_name: str | None = None


from schemas.user import UserRead


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


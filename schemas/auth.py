from enum import Enum

from pydantic import BaseModel


class AuthProvider(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"


class LoginRequest(BaseModel):
    token: str
    provider: AuthProvider
    full_name: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


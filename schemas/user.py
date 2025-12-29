from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    username: str
    is_active: bool
    balance: int
    gift_balance: int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBalanceUpdate(BaseModel):
    amount: int


class LeaderboardEntry(BaseModel):
    id: int
    username: str
    full_name: str | None
    cumulative_earned: int

    model_config = ConfigDict(from_attributes=True)

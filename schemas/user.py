from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    is_active: bool
    balance: int
    gift_balance: int
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserBalanceUpdate(BaseModel):
    amount: int


from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .user import UserRead


class RequestBase(BaseModel):
    amount: int
    description: str | None = None


class RequestCreate(RequestBase):
    recipient_id: int


class RequestRead(RequestBase):
    id: int
    sender_id: int
    recipient_id: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
    sender: UserRead
    recipient: UserRead

    model_config = ConfigDict(from_attributes=True)


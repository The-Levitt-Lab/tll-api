from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .user import UserRead


class RequestBase(BaseModel):
    amount: int
    description: Optional[str] = None


class RequestCreate(RequestBase):
    recipient_id: int


class RequestRead(RequestBase):
    id: int
    sender_id: int
    recipient_id: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    sender: UserRead
    recipient: UserRead

    class Config:
        from_attributes = True


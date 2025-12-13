from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    amount: int
    type: str
    description: str | None = None


class TransactionCreate(TransactionBase):
    user_id: int
    admin_id: int | None = None


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    # We might want to include the admin name if relevant, but let's keep it simple for now

    model_config = ConfigDict(from_attributes=True)


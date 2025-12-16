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
    recipient_id: int | None = None
    request_id: int | None = None
    shop_item_id: int | None = None


class TransferCreate(BaseModel):
    recipient_id: int
    amount: int
    description: str | None = None
    use_gift_balance: bool = False


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    user_name: str | None = None
    recipient_name: str | None = None
    shop_item_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

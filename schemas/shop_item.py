from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ShopItemBase(BaseModel):
    title: str
    description: str | None = None
    price: int
    image: str | None = None


class ShopItemCreate(ShopItemBase):
    pass


class ShopItemRead(ShopItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

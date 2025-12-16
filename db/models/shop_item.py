from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from db.base import Base


class ShopItem(Base):
    __tablename__ = "shop_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    image = Column(Text, nullable=True)  # Base64 encoded image
    created_at = Column(DateTime(timezone=True), server_default=func.now())

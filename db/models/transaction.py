from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
from db.models.user import User
from db.models.request import Request
from db.models.shop_item import ShopItem


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    amount = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=True)
    shop_item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], backref="transactions")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_transactions")
    request = relationship("Request", foreign_keys=[request_id], backref="transactions")
    shop_item = relationship("ShopItem", foreign_keys=[shop_item_id])
    admin = relationship(
        "User", foreign_keys=[admin_id], backref="administered_transactions"
    )

    @property
    def user_name(self):
        if self.user:
            return self.user.full_name or self.user.username
        return None

    @property
    def recipient_name(self):
        if self.recipient:
            return self.recipient.full_name or self.recipient.username
        return None

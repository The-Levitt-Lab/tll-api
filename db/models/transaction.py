from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
from db.models.user import User
from db.models.request import Request


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
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], backref="transactions")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_transactions")
    request = relationship("Request", foreign_keys=[request_id], backref="transactions")
    admin = relationship(
        "User", foreign_keys=[admin_id], backref="administered_transactions"
    )

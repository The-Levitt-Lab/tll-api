from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_user_id = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    balance = Column(Integer, default=25, nullable=False)
    gift_balance = Column(Integer, default=25, nullable=False)
    role = Column(String, default="student", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from db.base import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reward = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


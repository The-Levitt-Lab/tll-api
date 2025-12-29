from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChallengeBase(BaseModel):
    title: str
    description: str | None = None
    reward: int
    image: str | None = None


class ChallengeCreate(ChallengeBase):
    pass


class ChallengeRead(ChallengeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


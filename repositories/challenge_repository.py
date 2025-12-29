from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Challenge
from schemas.challenge import ChallengeCreate


async def get_challenges(
    session: AsyncSession, *, offset: int = 0, limit: int = 100
) -> List[Challenge]:
    result = await session.execute(
        select(Challenge)
        .order_by(Challenge.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_challenge(session: AsyncSession, challenge_in: ChallengeCreate) -> Challenge:
    challenge = Challenge(
        title=challenge_in.title,
        description=challenge_in.description,
        reward=challenge_in.reward,
        image=challenge_in.image,
    )
    session.add(challenge)
    await session.commit()
    await session.refresh(challenge)
    return challenge


async def delete_challenge(session: AsyncSession, challenge_id: int) -> bool:
    challenge = await session.get(Challenge, challenge_id)
    if challenge:
        await session.delete(challenge)
        await session.commit()
        return True
    return False


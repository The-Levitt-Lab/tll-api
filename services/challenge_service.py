from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Challenge
from repositories import challenge_repository
from schemas.challenge import ChallengeCreate

async def get_challenges(
    session: AsyncSession, offset: int = 0, limit: int = 100
) -> List[Challenge]:
    return await challenge_repository.get_challenges(session, offset=offset, limit=limit)

async def create_challenge(
    session: AsyncSession, challenge_in: ChallengeCreate
) -> Challenge:
    return await challenge_repository.create_challenge(session, challenge_in)


async def delete_challenge(session: AsyncSession, challenge_id: int) -> bool:
    return await challenge_repository.delete_challenge(session, challenge_id)

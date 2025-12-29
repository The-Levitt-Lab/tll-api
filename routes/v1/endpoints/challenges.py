from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_admin
from db.models import User
from db.session import get_db_session
from schemas.challenge import ChallengeCreate, ChallengeRead
from services import challenge_service

router = APIRouter()


@router.get("/", response_model=List[ChallengeRead])
async def read_challenges(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    """List all challenges (requires authentication)."""
    challenges = await challenge_service.get_challenges(session, offset=offset, limit=limit)
    return challenges


@router.post("/", response_model=ChallengeRead)
async def create_challenge(
    challenge_in: ChallengeCreate,
    session: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(require_admin),
):
    """Create a new challenge (admin only)."""
    return await challenge_service.create_challenge(session, challenge_in)


@router.delete("/{challenge_id}", response_model=bool)
async def delete_challenge(
    challenge_id: int,
    session: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(require_admin),
):
    """Delete a challenge (admin only)."""
    success = await challenge_service.delete_challenge(session, challenge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return success

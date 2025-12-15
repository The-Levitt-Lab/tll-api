from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Request


async def get_requests_by_user_id(
    db: AsyncSession, user_id: int, offset: int = 0, limit: int = 100
) -> list[Request]:
    stmt = (
        select(Request)
        .options(selectinload(Request.sender), selectinload(Request.recipient))
        .where(or_(Request.sender_id == user_id, Request.recipient_id == user_id))
        .order_by(Request.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


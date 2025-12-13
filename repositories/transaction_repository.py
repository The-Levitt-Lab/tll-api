from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Transaction
from schemas.transaction import TransactionCreate


async def get_transactions_by_user_id(
    session: AsyncSession, user_id: int, *, offset: int = 0, limit: int = 100
) -> List[Transaction]:
    result = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_transaction(session: AsyncSession, transaction_in: TransactionCreate) -> Transaction:
    transaction = Transaction(
        user_id=transaction_in.user_id,
        admin_id=transaction_in.admin_id,
        amount=transaction_in.amount,
        type=transaction_in.type,
        description=transaction_in.description,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction

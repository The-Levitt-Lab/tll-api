from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User, Transaction
from schemas.transaction import TransactionCreate, TransferCreate
from core.exceptions import NotFoundError, BadRequestError

async def transfer_funds_service(session: AsyncSession, transfer_in: TransferCreate, sender_id: int):
    if transfer_in.recipient_id == sender_id:
        raise BadRequestError("Cannot send money to yourself")

    if transfer_in.amount <= 0:
        raise BadRequestError("Amount must be positive")

    # Fetch sender
    stmt_sender = select(User).where(User.id == sender_id)
    result_sender = await session.execute(stmt_sender)
    sender = result_sender.scalars().first()
    
    if not sender:
        raise NotFoundError("Sender not found")
        
    if sender.balance < transfer_in.amount:
        raise BadRequestError("Insufficient balance")

    # Fetch recipient
    stmt_recipient = select(User).where(User.id == transfer_in.recipient_id)
    result_recipient = await session.execute(stmt_recipient)
    recipient = result_recipient.scalars().first()
    
    if not recipient:
        raise NotFoundError("Recipient not found")
        
    # Update balances
    sender.balance -= transfer_in.amount
    recipient.balance += transfer_in.amount
    
    session.add(sender)
    session.add(recipient)
    
    # Create transaction for Sender (Debit)
    debit_tx = Transaction(
        user_id=sender_id,
        amount=-transfer_in.amount,
        type="transfer",
        description=f"Sent to {recipient.full_name or recipient.username}: {transfer_in.description or 'No description'}",
        recipient_id=transfer_in.recipient_id
    )
    session.add(debit_tx)

    # Create transaction for Recipient (Credit)
    credit_tx = Transaction(
        user_id=recipient.id,
        amount=transfer_in.amount,
        type="transfer_received",
        description=f"Received from {sender.full_name or sender.username}: {transfer_in.description or 'No description'}",
        recipient_id=sender_id
    )
    session.add(credit_tx)
    
    await session.commit()
    await session.refresh(debit_tx)
    
    return debit_tx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import Request, User
from repositories.transaction_repository import create_transaction
from schemas.transaction import TransactionCreate
from schemas.request import RequestCreate
from core.exceptions import NotFoundError, ForbiddenError, BadRequestError

async def create_request_service(session: AsyncSession, request_in: RequestCreate, sender_id: int):
    # Check if recipient exists
    stmt = select(User).where(User.id == request_in.recipient_id)
    result = await session.execute(stmt)
    recipient = result.scalars().first()
    
    if not recipient:
        raise NotFoundError("Recipient not found")
        
    if request_in.recipient_id == sender_id:
        raise BadRequestError("Cannot send request to yourself")
        
    request = Request(
        sender_id=sender_id,
        recipient_id=request_in.recipient_id,
        amount=request_in.amount,
        description=request_in.description,
        status="pending",
        is_active=True
    )
    
    session.add(request)
    await session.commit()
    await session.refresh(request)
    
    return request

async def pay_request_service(session: AsyncSession, request_id: int, user_id: int):
    # Fetch request
    stmt = select(Request).where(Request.id == request_id)
    result = await session.execute(stmt)
    request = result.scalars().first()
    
    if not request:
        raise NotFoundError(f"Request {request_id} not found")
        
    if request.recipient_id != user_id:
        raise ForbiddenError("You are not the recipient of this request")
        
    if not request.is_active:
        raise BadRequestError("Request is already paid or inactive")
        
    # Check balance
    stmt_user = select(User).where(User.id == user_id)
    result_user = await session.execute(stmt_user)
    payer = result_user.scalars().first()
    
    if not payer:
         raise NotFoundError("User not found")
         
    if payer.balance < request.amount:
        raise BadRequestError("Insufficient balance")
        
    # Update balances
    payer.balance -= request.amount
    session.add(payer)
    
    stmt_recipient = select(User).where(User.id == request.sender_id)
    result_recipient = await session.execute(stmt_recipient)
    payee = result_recipient.scalars().first()
    
    if payee:
        payee.balance += request.amount
        session.add(payee)
    
    # Create transaction for Payer (Debit)
    debit_transaction = TransactionCreate(
        user_id=user_id,
        amount=-request.amount,
        type="request_payment",
        description=request.description or 'No description',
        recipient_id=request.sender_id,
        request_id=request.id
    )
    await create_transaction(session, debit_transaction)

    # Create transaction for Payee (Credit)
    if payee:
        credit_transaction = TransactionCreate(
            user_id=payee.id,
            amount=request.amount,
            type="request_payment_received",
            description=request.description or 'No description',
            recipient_id=user_id,
            request_id=request.id
        )
        await create_transaction(session, credit_transaction)
    
    # Update request
    request.is_active = False
    request.status = "completed"
    session.add(request)
    
    await session.commit()
    return request

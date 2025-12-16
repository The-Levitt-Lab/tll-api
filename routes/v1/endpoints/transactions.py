from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from db.models import User
from db.session import get_db_session
from schemas.transaction import TransactionRead, TransferCreate
from services import (
    NotFoundError,
    transfer_funds_service,
)
from core.exceptions import BadRequestError

router = APIRouter()

@router.post("/transfer", response_model=TransactionRead)
async def transfer_funds(
    transfer_in: TransferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        # We need to await the service call
        # The service returns a TransactionCreate object (pydantic), not ORM object, because create_transaction returns the pydantic model?
        # Let's check repository.
        # Actually, repositories/transaction_repository.py likely returns ORM object.
        # But schemas/transaction.py TransactionCreate is pydantic.
        # services/transaction_service.py calls create_transaction and awaits it.
        # We need to make sure the return type matches TransactionRead.
        
        # Checking services/transaction_service.py again:
        # It creates `debit_transaction` (TransactionCreate pydantic)
        # passes it to `create_transaction`
        # returns `debit_transaction` (TransactionCreate)
        
        # TransactionCreate has amount, type, description, user_id, recipient_id, etc.
        # TransactionRead has id, created_at, user_name, recipient_name.
        # TransactionCreate DOES NOT have id, created_at.
        
        # So services/transaction_service.py needs to return the created ORM object or fetch it.
        # I need to fix services/transaction_service.py first.
        
        return await transfer_funds_service(db, transfer_in, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Recipient not found")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        
        return await transfer_funds_service(db, transfer_in, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Recipient not found")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))

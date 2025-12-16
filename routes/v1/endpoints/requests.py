from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from db.models import User
from db.session import get_db_session
from schemas.request import RequestRead, RequestCreate
from services import (
    NotFoundError,
    pay_request_service,
    create_request_service,
)
from core.exceptions import ForbiddenError, BadRequestError

router = APIRouter()

@router.post("/", response_model=RequestRead, status_code=201)
async def create_request(
    request_in: RequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await create_request_service(db, request_in, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Recipient not found")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{request_id}/pay", response_model=RequestRead)
async def pay_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await pay_request_service(db, request_id, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Request not found")
    except ForbiddenError:
        raise HTTPException(status_code=403, detail="You are not authorized to pay this request")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


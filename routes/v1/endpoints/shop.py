from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from core.dependencies import get_current_user, require_admin
from db.models import User
from schemas.shop_item import ShopItemRead, ShopItemCreate
from schemas.transaction import TransactionRead
from services.shop_service import ShopService

router = APIRouter()


@router.get("/", response_model=list[ShopItemRead])
async def list_shop_items(
    db: AsyncSession = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    """List all available shop items (requires authentication)."""
    service = ShopService(db)
    return await service.list_items()


@router.post("/", response_model=ShopItemRead, status_code=status.HTTP_201_CREATED)
async def create_shop_item(
    item_data: ShopItemCreate,
    db: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(require_admin),
):
    """Create a new shop item (admin only)."""
    service = ShopService(db)
    return await service.create_item(item_data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shop_item(
    item_id: int,
    db: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(require_admin),
):
    """Delete a shop item (admin only)."""
    service = ShopService(db)
    await service.delete_item(item_id)


@router.post("/{item_id}/purchase", response_model=TransactionRead)
async def purchase_shop_item(
    item_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Purchase a shop item (requires authentication)."""
    service = ShopService(db)
    return await service.purchase_item(current_user.id, item_id)

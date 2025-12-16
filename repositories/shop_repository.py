from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.shop_item import ShopItem


class ShopRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[ShopItem]:
        stmt = select(ShopItem)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, item_id: int) -> ShopItem | None:
        stmt = select(ShopItem).where(ShopItem.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create(self, item: ShopItem) -> ShopItem:
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete(self, item: ShopItem) -> None:
        await self.session.delete(item)
        await self.session.flush()

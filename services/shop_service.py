from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Transaction, ShopItem
from core.exceptions import NotFoundError, BadRequestError
from repositories.shop_repository import ShopRepository
from schemas.shop_item import ShopItemCreate


class ShopService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ShopRepository(session)

    async def list_items(self) -> list[ShopItem]:
        return await self.repository.get_all()

    async def create_item(self, item_data: ShopItemCreate) -> ShopItem:
        item = ShopItem(**item_data.model_dump())
        item = await self.repository.create(item)
        await self.session.commit()
        return item

    async def delete_item(self, item_id: int) -> None:
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundError("Shop item not found")
        
        await self.repository.delete(item)
        await self.session.commit()

    async def purchase_item(self, user_id: int, item_id: int) -> Transaction:
        # 1. Fetch item
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundError("Shop item not found")

        # 2. Fetch user (using session directly or user repo if available, trying session for now)
        user = await self.session.get(User, user_id)
        if not user:
            raise NotFoundError("User not found")

        # 3. Check balance
        if user.balance < item.price:
            raise BadRequestError(f"Insufficient funds. Item costs {item.price}, you have {user.balance}")

        # 4. Deduct balance
        user.balance -= item.price
        self.session.add(user)

        # 5. Create Transaction
        transaction = Transaction(
            user_id=user.id,
            amount=-item.price,
            type="shop_purchase",
            description=f"Purchased: {item.title}",
            shop_item_id=item.id
        )
        self.session.add(transaction)

        # 6. Commit
        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

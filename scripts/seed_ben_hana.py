import asyncio
import random
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from db.session import AsyncSessionLocal
from db.models.user import User
from db.models.transaction import Transaction
from db.models.request import Request

async def main():
    async with AsyncSessionLocal() as session:
        print("Starting seed script...")
        
        # Clear existing data
        print("Clearing existing transactions and requests...")
        await session.execute(delete(Transaction))
        await session.execute(delete(Request))
        await session.commit()
        print("Cleared.")

        # Fetch users
        print("Fetching users...")
        ben_stmt = select(User).where(User.email == "benklosky@uchicago.edu")
        hana_stmt = select(User).where(User.email == "horiuchih@uchicago.edu")
        
        result_ben = await session.execute(ben_stmt)
        ben = result_ben.scalar_one_or_none()
        
        result_hana = await session.execute(hana_stmt)
        hana = result_hana.scalar_one_or_none()

        if not ben or not hana:
            print("Error: Could not find Ben or Hana. Please ensure users are seeded in the database.")
            print(f"Ben found: {ben is not None}")
            print(f"Hana found: {hana is not None}")
            return

        print(f"Found Ben (id={ben.id}) and Hana (id={hana.id})")

        descriptions = [
            "movie tickets", "coffee", "lunch at cafe", "dinner", 
            "groceries", "utilities share", "rent split", "snacks",
            "concert tickets", "drinks", "taxi ride", "gift",
            "book", "gym membership"
        ]

        # Generate Transactions
        print("Generating transactions...")
        transactions = []
        now = datetime.now()
        start_date = now - timedelta(days=30)
        
        # 20 transactions
        for i in range(20):
            # Random time in last 30 days
            days_offset = random.randint(0, 30)
            # Random seconds in the day
            seconds_offset = random.randint(0, 86400)
            txn_time = start_date + timedelta(days=days_offset, seconds=seconds_offset)
            
            # Ensure we don't go into future
            if txn_time > now:
                txn_time = now - timedelta(minutes=random.randint(1, 60))

            # Randomize direction
            if random.random() > 0.5:
                sender = ben
                recipient = hana
            else:
                sender = hana
                recipient = ben
            
            amount = random.randint(5, 50)
            description = random.choice(descriptions)
            
            txn = Transaction(
                user_id=sender.id,
                recipient_id=recipient.id,
                amount=amount,
                type="transfer",
                description=description,
                created_at=txn_time
            )
            transactions.append(txn)
            
        session.add_all(transactions)
        
        # Generate Requests
        print("Generating requests...")
        requests = []
        for i in range(10):
            # Random time in last 30 days
            days_offset = random.randint(0, 30)
            seconds_offset = random.randint(0, 86400)
            req_time = start_date + timedelta(days=days_offset, seconds=seconds_offset)

            if req_time > now:
                req_time = now - timedelta(minutes=random.randint(1, 60))
            
            if random.random() > 0.5:
                sender = ben
                recipient = hana
            else:
                sender = hana
                recipient = ben
                
            amount = random.randint(5, 50)
            description = random.choice(descriptions)
            
            req = Request(
                sender_id=sender.id,
                recipient_id=recipient.id,
                amount=amount,
                status="pending",
                is_active=True,
                description=description,
                created_at=req_time,
                updated_at=req_time
            )
            requests.append(req)
            
        session.add_all(requests)
        
        await session.commit()
        print(f"Successfully created {len(transactions)} transactions and {len(requests)} requests.")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")

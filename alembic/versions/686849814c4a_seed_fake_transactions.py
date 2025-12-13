"""seed_fake_transactions

Revision ID: 686849814c4a
Revises: 7f99731087ee
Create Date: 2025-12-12 15:47:23.368748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '686849814c4a'
down_revision: Union[str, Sequence[str], None] = '7f99731087ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Transactions for Ben Klosky (net: +150)
BEN_TRANSACTIONS = [
    (50, 'earn', 'Completed weekly challenge: Most steps'),
    (25, 'earn', 'Referral bonus'),
    (-15, 'spend', 'Purchased coffee voucher'),
    (100, 'earn', 'Won trivia night'),
    (30, 'earn', 'Perfect attendance bonus'),
    (-20, 'spend', 'Donated to charity pool'),
    (-10, 'spend', 'Snack bar purchase'),
    (-10, 'spend', 'Lost a bet to Hana'),
]

# Transactions for Hana Horiuchi (net: +85)
HANA_TRANSACTIONS = [
    (75, 'earn', 'First place in coding challenge'),
    (20, 'earn', 'Helped a teammate'),
    (-30, 'spend', 'Purchased movie tickets'),
    (10, 'earn', 'Won bet against Ben'),
    (50, 'earn', 'Monthly top performer'),
    (-25, 'spend', 'Team lunch contribution'),
    (-15, 'spend', 'Gym membership fee'),
]


def upgrade() -> None:
    """Upgrade schema."""
    # Get user IDs for Ben and Hana
    conn = op.get_bind()
    
    ben_result = conn.execute(
        sa.text("SELECT id FROM users WHERE email = 'benklosky@uchicago.edu'")
    ).fetchone()
    hana_result = conn.execute(
        sa.text("SELECT id FROM users WHERE email = 'horiuchih@uchicago.edu'")
    ).fetchone()
    
    if not ben_result or not hana_result:
        raise Exception("Ben Klosky or Hana Horiuchi not found in users table")
    
    ben_id = ben_result[0]
    hana_id = hana_result[0]
    
    # Insert transactions for Ben (some with Hana as admin, some with himself)
    ben_balance = 0
    for i, (amount, tx_type, description) in enumerate(BEN_TRANSACTIONS):
        admin_id = hana_id if i % 2 == 0 else ben_id
        conn.execute(
            sa.text("""
                INSERT INTO transactions (user_id, admin_id, amount, type, description, created_at)
                VALUES (:user_id, :admin_id, :amount, :type, :description, 
                        NOW() - INTERVAL ':days days' - INTERVAL ':hours hours')
            """.replace(':days', str(len(BEN_TRANSACTIONS) - i)).replace(':hours', str(i * 2))),
            {
                'user_id': ben_id,
                'admin_id': admin_id,
                'amount': amount,
                'type': tx_type,
                'description': description,
            }
        )
        ben_balance += amount
    
    # Insert transactions for Hana (some with Ben as admin, some with herself)
    hana_balance = 0
    for i, (amount, tx_type, description) in enumerate(HANA_TRANSACTIONS):
        admin_id = ben_id if i % 2 == 0 else hana_id
        conn.execute(
            sa.text("""
                INSERT INTO transactions (user_id, admin_id, amount, type, description, created_at)
                VALUES (:user_id, :admin_id, :amount, :type, :description,
                        NOW() - INTERVAL ':days days' - INTERVAL ':hours hours')
            """.replace(':days', str(len(HANA_TRANSACTIONS) - i)).replace(':hours', str(i * 3))),
            {
                'user_id': hana_id,
                'admin_id': admin_id,
                'amount': amount,
                'type': tx_type,
                'description': description,
            }
        )
        hana_balance += amount
    
    # Update balances
    conn.execute(
        sa.text("UPDATE users SET balance = :balance WHERE id = :user_id"),
        {'balance': ben_balance, 'user_id': ben_id}
    )
    conn.execute(
        sa.text("UPDATE users SET balance = :balance WHERE id = :user_id"),
        {'balance': hana_balance, 'user_id': hana_id}
    )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    
    # Get user IDs
    ben_result = conn.execute(
        sa.text("SELECT id FROM users WHERE email = 'benklosky@uchicago.edu'")
    ).fetchone()
    hana_result = conn.execute(
        sa.text("SELECT id FROM users WHERE email = 'horiuchih@uchicago.edu'")
    ).fetchone()
    
    if ben_result:
        conn.execute(
            sa.text("DELETE FROM transactions WHERE user_id = :user_id"),
            {'user_id': ben_result[0]}
        )
        conn.execute(
            sa.text("UPDATE users SET balance = 0 WHERE id = :user_id"),
            {'user_id': ben_result[0]}
        )
    
    if hana_result:
        conn.execute(
            sa.text("DELETE FROM transactions WHERE user_id = :user_id"),
            {'user_id': hana_result[0]}
        )
        conn.execute(
            sa.text("UPDATE users SET balance = 0 WHERE id = :user_id"),
            {'user_id': hana_result[0]}
        )

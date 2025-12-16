"""seed_sample_shop_items

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-16 15:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO shop_items (title, description, price, image)
        VALUES 
            ('Vittcoin Sticker', 'A cool holographic Vittcoin sticker for your laptop', 10, NULL),
            ('Coffee Voucher', 'Redeem for one free coffee at the campus cafe', 25, NULL);
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM shop_items 
        WHERE title IN ('Vittcoin Sticker', 'Coffee Voucher');
    """)


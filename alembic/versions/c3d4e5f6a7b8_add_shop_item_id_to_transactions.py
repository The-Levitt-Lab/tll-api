"""add_shop_item_id_to_transactions

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-12-16 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transactions', sa.Column('shop_item_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'transactions', 'shop_items', ['shop_item_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'shop_item_id')

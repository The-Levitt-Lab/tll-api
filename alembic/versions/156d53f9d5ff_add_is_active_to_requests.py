"""add_is_active_to_requests

Revision ID: 156d53f9d5ff
Revises: 1313e372e398
Create Date: 2025-12-15 16:21:50.516549

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '156d53f9d5ff'
down_revision: Union[str, Sequence[str], None] = '1313e372e398'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('requests', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('requests', 'is_active')

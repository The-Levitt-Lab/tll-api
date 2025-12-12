"""populate_username

Revision ID: 960907d33978
Revises: c1f2a822a35b
Create Date: 2025-12-12 12:04:37.822449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '960907d33978'
down_revision: Union[str, Sequence[str], None] = 'c1f2a822a35b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE users SET username = '@' || lower(regexp_replace(trim(full_name), '\\s+', '.', 'g'))")
    op.alter_column('users', 'username', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'username', nullable=True)
    op.execute("UPDATE users SET username = NULL")

"""seed_admin_users

Revision ID: 7f99731087ee
Revises: 960907d33978
Create Date: 2025-12-12 12:51:59.506162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f99731087ee'
down_revision: Union[str, Sequence[str], None] = '960907d33978'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO users (full_name, username, email, balance, gift_balance, role, is_active)
        VALUES 
            ('Ben Klosky', '@ben.klosky', 'benklosky@uchicago.edu', 0, 25, 'admin', true),
            ('Hana Horiuchi', '@hana.horiuchi', 'horiuchih@uchicago.edu', 0, 25, 'admin', true)
        ON CONFLICT (email) DO UPDATE SET role = 'admin'
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DELETE FROM users 
        WHERE email IN ('benklosky@uchicago.edu', 'horiuchih@uchicago.edu')
    """)

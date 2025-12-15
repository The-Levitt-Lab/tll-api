"""seed_sample_request

Revision ID: 1313e372e398
Revises: 9dbc1558647d
Create Date: 2025-12-15 15:37:57.754028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1313e372e398'
down_revision: Union[str, Sequence[str], None] = '9dbc1558647d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO requests (sender_id, recipient_id, amount, status, description, created_at)
        SELECT s.id, r.id, 5, 'pending', 'Coffee', NOW()
        FROM users s, users r
        WHERE s.email = 'benklosky@uchicago.edu' AND r.email = 'horiuchih@uchicago.edu'
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DELETE FROM requests
        WHERE sender_id = (SELECT id FROM users WHERE email = 'benklosky@uchicago.edu')
        AND recipient_id = (SELECT id FROM users WHERE email = 'horiuchih@uchicago.edu')
        AND description = 'Coffee'
    """)

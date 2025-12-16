"""seed_test_request_hana_to_ben

Revision ID: 8293b020ced7
Revises: 156d53f9d5ff
Create Date: 2025-12-16 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8293b020ced7'
down_revision: Union[str, Sequence[str], None] = '156d53f9d5ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO requests (sender_id, recipient_id, amount, status, description, is_active, created_at, updated_at)
        VALUES (
            (SELECT id FROM users WHERE email = 'horiuchih@uchicago.edu'),
            (SELECT id FROM users WHERE email = 'benklosky@uchicago.edu'),
            10,
            'pending',
            'Test request from Hana to Ben',
            true,
            NOW(),
            NOW()
        );
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM requests 
        WHERE sender_id = (SELECT id FROM users WHERE email = 'horiuchih@uchicago.edu')
        AND recipient_id = (SELECT id FROM users WHERE email = 'benklosky@uchicago.edu')
        AND description = 'Test request from Hana to Ben';
    """)

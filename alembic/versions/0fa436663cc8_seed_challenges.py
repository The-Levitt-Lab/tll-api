"""seed_challenges

Revision ID: 0fa436663cc8
Revises: c3d4e5f6a7b8
Create Date: 2025-12-16 16:44:42.036510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '0fa436663cc8'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    challenges_table = sa.table(
        'challenges',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('reward', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now())
    )

    op.bulk_insert(
        challenges_table,
        [
            {
                "title": "Math Whiz",
                "description": "Make 10% progress in math in a week",
                "reward": 50
            },
            {
                "title": "Consistent Learner",
                "description": "Complete 5 lessons in a single day",
                "reward": 30
            },
            {
                "title": "Weekly Warrior",
                "description": "Log in every day for a week",
                "reward": 100
            }
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM challenges WHERE title IN ('Math Whiz', 'Consistent Learner', 'Weekly Warrior')")

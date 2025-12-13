"""add_requests_table

Revision ID: e4d3c2b1a0f9
Revises: 686849814c4a
Create Date: 2025-12-12 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4d3c2b1a0f9'
down_revision: Union[str, Sequence[str], None] = '686849814c4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create requests table
    op.create_table('requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], name='fk_requests_sender_id'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], name='fk_requests_recipient_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_id'), 'requests', ['id'], unique=False)

    # Update transactions table
    op.add_column('transactions', sa.Column('recipient_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('request_id', sa.Integer(), nullable=True))
    
    # Naming constraints explicitly for easier downgrade
    op.create_foreign_key('fk_transactions_recipient_id', 'transactions', 'users', ['recipient_id'], ['id'])
    op.create_foreign_key('fk_transactions_request_id', 'transactions', 'requests', ['request_id'], ['id'])


def downgrade() -> None:
    # Remove columns from transactions
    op.drop_constraint('fk_transactions_request_id', 'transactions', type_='foreignkey')
    op.drop_constraint('fk_transactions_recipient_id', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'request_id')
    op.drop_column('transactions', 'recipient_id')

    # Drop requests table
    op.drop_index(op.f('ix_requests_id'), table_name='requests')
    op.drop_table('requests')


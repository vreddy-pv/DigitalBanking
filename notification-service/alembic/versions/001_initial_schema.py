"""Initial schema creation for notifications table

Revision ID: 001
Revises:
Create Date: 2026-05-08 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_type', sa.String(length=20), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_notifications_transaction_id', 'notifications', ['transaction_id'])
    op.create_index('idx_notifications_status', 'notifications', ['status'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_notifications_created_at', table_name='notifications')
    op.drop_index('idx_notifications_status', table_name='notifications')
    op.drop_index('idx_notifications_transaction_id', table_name='notifications')

    # Drop table
    op.drop_table('notifications')

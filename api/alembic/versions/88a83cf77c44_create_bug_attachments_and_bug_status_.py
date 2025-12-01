"""create_bug_attachments_and_bug_status_history_tables

Revision ID: 88a83cf77c44
Revises: f1b556feb80f
Create Date: 2025-11-15 18:00:36.310338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88a83cf77c44'
down_revision: Union[str, Sequence[str], None] = 'f1b556feb80f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create bug_attachments table
    op.create_table(
        'bug_attachments',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('bug_id', sa.String(20), sa.ForeignKey('bugs.id'), nullable=False),
        
        # File details
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=True),  # image/png, application/pdf, etc.
        sa.Column('file_size', sa.Integer, nullable=True),  # in bytes
        
        # Audit fields
        sa.Column('uploaded_by', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false')
    )
    
    # Create index for bug_attachments
    op.create_index('idx_bug_attachments_bug', 'bug_attachments', ['bug_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    
    # Create bug_status_history table
    op.create_table(
        'bug_status_history',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('bug_id', sa.String(20), sa.ForeignKey('bugs.id'), nullable=False),
        
        # Status change
        sa.Column('from_status', sa.String(50), nullable=True),
        sa.Column('to_status', sa.String(50), nullable=False),
        sa.Column('resolution_type', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        
        # Audit fields
        sa.Column('changed_by', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes for bug_status_history
    op.create_index('idx_bug_status_history_bug', 'bug_status_history', ['bug_id'])
    op.create_index('idx_bug_status_history_date', 'bug_status_history', ['changed_at'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop bug_status_history table and indexes
    op.drop_index('idx_bug_status_history_date', table_name='bug_status_history')
    op.drop_index('idx_bug_status_history_bug', table_name='bug_status_history')
    op.drop_table('bug_status_history')
    
    # Drop bug_attachments table and index
    op.drop_index('idx_bug_attachments_bug', table_name='bug_attachments')
    op.drop_table('bug_attachments')

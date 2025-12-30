"""create_comments_tables

Revision ID: f1b556feb80f
Revises: 535f255e9098
Create Date: 2025-11-15 18:00:07.727445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1b556feb80f'
down_revision: Union[str, Sequence[str], None] = '535f255e9098'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create bug_comments table
    op.create_table(
        'bug_comments',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('bug_id', sa.String(20), sa.ForeignKey('bugs.id'), nullable=False),
        
        # Comment details
        sa.Column('comment_text', sa.Text, nullable=False),
        sa.Column('author_id', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        
        # Mentions
        sa.Column('mentioned_users', sa.Text, nullable=True),  # JSON array of user IDs
        
        # Edit tracking
        sa.Column('is_edited', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        
        # Attachments
        sa.Column('attachments', sa.Text, nullable=True),  # JSON array of file paths
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false')
    )
    
    # Create indexes for bug_comments
    op.create_index('idx_bug_comments_bug', 'bug_comments', ['bug_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_bug_comments_author', 'bug_comments', ['author_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_bug_comments_created', 'bug_comments', ['created_at'])
    
    # Create test_case_comments table
    op.create_table(
        'test_case_comments',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('test_case_id', sa.String(20), sa.ForeignKey('test_cases.id'), nullable=False),
        
        # Comment details
        sa.Column('comment_text', sa.Text, nullable=False),
        sa.Column('author_id', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        
        # Mentions
        sa.Column('mentioned_users', sa.Text, nullable=True),  # JSON array of user IDs
        
        # Edit tracking
        sa.Column('is_edited', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        
        # Attachments
        sa.Column('attachments', sa.Text, nullable=True),  # JSON array of file paths
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false')
    )
    
    # Create indexes for test_case_comments
    op.create_index('idx_test_case_comments_test_case', 'test_case_comments', ['test_case_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_case_comments_author', 'test_case_comments', ['author_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_case_comments_created', 'test_case_comments', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop test_case_comments table and indexes
    op.drop_index('idx_test_case_comments_created', table_name='test_case_comments')
    op.drop_index('idx_test_case_comments_author', table_name='test_case_comments')
    op.drop_index('idx_test_case_comments_test_case', table_name='test_case_comments')
    op.drop_table('test_case_comments')
    
    # Drop bug_comments table and indexes
    op.drop_index('idx_bug_comments_created', table_name='bug_comments')
    op.drop_index('idx_bug_comments_author', table_name='bug_comments')
    op.drop_index('idx_bug_comments_bug', table_name='bug_comments')
    op.drop_table('bug_comments')

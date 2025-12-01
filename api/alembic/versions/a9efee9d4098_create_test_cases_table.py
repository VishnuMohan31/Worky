"""create_test_cases_table

Revision ID: a9efee9d4098
Revises: 83469924c36b
Create Date: 2025-11-15 17:58:14.384975

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9efee9d4098'
down_revision: Union[str, Sequence[str], None] = '83469924c36b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create test_cases table
    op.create_table(
        'test_cases',
        sa.Column('id', sa.String(20), primary_key=True),
        
        # Hierarchy associations (nullable, only one should be set)
        sa.Column('project_id', sa.String(20), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('usecase_id', sa.String(20), sa.ForeignKey('usecases.id'), nullable=True),
        sa.Column('user_story_id', sa.String(20), sa.ForeignKey('user_stories.id'), nullable=True),
        sa.Column('task_id', sa.String(20), sa.ForeignKey('tasks.id'), nullable=True),
        
        # Test case details
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('preconditions', sa.Text, nullable=True),
        sa.Column('test_steps', sa.Text, nullable=False),  # JSON array of steps
        sa.Column('expected_result', sa.Text, nullable=False),
        sa.Column('test_data', sa.Text, nullable=True),  # JSON for test data
        
        # Classification
        sa.Column('test_type', sa.String(50), nullable=False),  # Functional, Integration, Regression, etc.
        sa.Column('priority', sa.String(20), nullable=False),  # P0, P1, P2, P3
        sa.Column('status', sa.String(50), nullable=False, server_default='Draft'),  # Draft, Ready for Review, Approved, Active, Deprecated, Obsolete
        
        # Versioning
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('tags', sa.Text, nullable=True),  # JSON array of tags
        
        # Audit fields
        sa.Column('created_by', sa.String(20), nullable=False),
        sa.Column('updated_by', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        
        # Constraint to ensure only one hierarchy level is set
        sa.CheckConstraint(
            """
            (project_id IS NOT NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NOT NULL AND user_story_id IS NULL AND task_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NOT NULL AND task_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NOT NULL)
            """,
            name='test_case_hierarchy_check'
        )
    )
    
    # Create indexes for hierarchy relationships and status
    op.create_index('idx_test_cases_project', 'test_cases', ['project_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_cases_usecase', 'test_cases', ['usecase_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_cases_user_story', 'test_cases', ['user_story_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_cases_task', 'test_cases', ['task_id'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_cases_status', 'test_cases', ['status'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_cases_type', 'test_cases', ['test_type'], 
                    postgresql_where=sa.text('is_deleted = false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_test_cases_type', table_name='test_cases')
    op.drop_index('idx_test_cases_status', table_name='test_cases')
    op.drop_index('idx_test_cases_task', table_name='test_cases')
    op.drop_index('idx_test_cases_user_story', table_name='test_cases')
    op.drop_index('idx_test_cases_usecase', table_name='test_cases')
    op.drop_index('idx_test_cases_project', table_name='test_cases')
    
    # Drop table
    op.drop_table('test_cases')

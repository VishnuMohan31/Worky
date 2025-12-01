"""create_test_case_bugs_junction_table

Revision ID: 535f255e9098
Revises: 1a26bb8a63b7
Create Date: 2025-11-15 17:59:45.571883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '535f255e9098'
down_revision: Union[str, Sequence[str], None] = '1a26bb8a63b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create test_case_bugs junction table
    op.create_table(
        'test_case_bugs',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('test_case_id', sa.String(20), sa.ForeignKey('test_cases.id'), nullable=False),
        sa.Column('bug_id', sa.String(20), sa.ForeignKey('bugs.id'), nullable=False),
        sa.Column('test_execution_id', sa.String(20), sa.ForeignKey('test_executions.id'), nullable=True),  # Which execution found the bug
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(20), nullable=False),
        
        # Unique constraint on (test_case_id, bug_id)
        sa.UniqueConstraint('test_case_id', 'bug_id', name='uq_test_case_bug')
    )
    
    # Create indexes
    op.create_index('idx_test_case_bugs_test_case', 'test_case_bugs', ['test_case_id'])
    op.create_index('idx_test_case_bugs_bug', 'test_case_bugs', ['bug_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_test_case_bugs_bug', table_name='test_case_bugs')
    op.drop_index('idx_test_case_bugs_test_case', table_name='test_case_bugs')
    
    # Drop table
    op.drop_table('test_case_bugs')

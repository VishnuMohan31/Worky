"""create_test_executions_and_test_runs_tables

Revision ID: 71458e0c66fb
Revises: a9efee9d4098
Create Date: 2025-11-15 17:58:46.168728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71458e0c66fb'
down_revision: Union[str, Sequence[str], None] = 'a9efee9d4098'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create test_runs table first (since test_executions references it)
    op.create_table(
        'test_runs',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        
        # Association (sprint_id without FK constraint due to type mismatch in existing schema)
        sa.Column('sprint_id', sa.String(50), nullable=True),  # No FK constraint
        sa.Column('release_version', sa.String(50), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='In Progress'),  # In Progress, Completed, Aborted
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        
        # Metrics (calculated)
        sa.Column('total_tests', sa.Integer, nullable=False, server_default='0'),
        sa.Column('passed_tests', sa.Integer, nullable=False, server_default='0'),
        sa.Column('failed_tests', sa.Integer, nullable=False, server_default='0'),
        sa.Column('blocked_tests', sa.Integer, nullable=False, server_default='0'),
        sa.Column('skipped_tests', sa.Integer, nullable=False, server_default='0'),
        
        # Audit fields
        sa.Column('created_by', sa.String(20), nullable=False),
        sa.Column('updated_by', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false')
    )
    
    # Create indexes for test_runs
    op.create_index('idx_test_runs_status', 'test_runs', ['status'], 
                    postgresql_where=sa.text('is_deleted = false'))
    op.create_index('idx_test_runs_sprint', 'test_runs', ['sprint_id'])
    
    # Create test_executions table
    op.create_table(
        'test_executions',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('test_case_id', sa.String(20), sa.ForeignKey('test_cases.id'), nullable=False),
        sa.Column('test_run_id', sa.String(20), sa.ForeignKey('test_runs.id'), nullable=True),  # Optional grouping
        
        # Execution details
        sa.Column('executed_by', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('execution_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('execution_status', sa.String(50), nullable=False),  # Passed, Failed, Blocked, Skipped, Not Applicable
        sa.Column('actual_result', sa.Text, nullable=True),
        sa.Column('execution_notes', sa.Text, nullable=True),
        
        # Environment
        sa.Column('environment', sa.String(100), nullable=True),  # e.g., "Chrome 120, Windows 11"
        sa.Column('browser', sa.String(50), nullable=True),
        sa.Column('os', sa.String(50), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        
        # Attachments
        sa.Column('screenshots', sa.Text, nullable=True),  # JSON array of file paths
        sa.Column('log_files', sa.Text, nullable=True),  # JSON array of file paths
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    
    # Create indexes for test_executions
    op.create_index('idx_test_executions_test_case', 'test_executions', ['test_case_id'])
    op.create_index('idx_test_executions_status', 'test_executions', ['execution_status'])
    op.create_index('idx_test_executions_date', 'test_executions', ['execution_date'])
    op.create_index('idx_test_executions_executor', 'test_executions', ['executed_by'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop test_executions table and indexes first
    op.drop_index('idx_test_executions_executor', table_name='test_executions')
    op.drop_index('idx_test_executions_date', table_name='test_executions')
    op.drop_index('idx_test_executions_status', table_name='test_executions')
    op.drop_index('idx_test_executions_test_case', table_name='test_executions')
    op.drop_table('test_executions')
    
    # Drop test_runs table and indexes
    op.drop_index('idx_test_runs_sprint', table_name='test_runs')
    op.drop_index('idx_test_runs_status', table_name='test_runs')
    op.drop_table('test_runs')

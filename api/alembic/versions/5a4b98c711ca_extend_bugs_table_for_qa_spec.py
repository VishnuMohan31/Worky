"""extend_bugs_table_for_qa_spec

Revision ID: 5a4b98c711ca
Revises: 05fb4fcf5df1
Create Date: 2025-11-16 16:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a4b98c711ca'
down_revision: Union[str, Sequence[str], None] = '05fb4fcf5df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Extend bugs table with QA spec fields."""
    # Add test_run_id and test_case_id for bugs from test failures
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS test_run_id VARCHAR(20) REFERENCES test_runs(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS test_case_id VARCHAR(20) REFERENCES test_cases(id)")
    
    # Add category, severity, priority, status fields
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS category VARCHAR(50)")  # UI, Backend, Database, Integration, Performance, Security, Environment
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS severity VARCHAR(50)")  # Critical, High, Medium, Low
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS priority VARCHAR(50)")  # P1, P2, P3, P4
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'New'")  # New, Open, In Progress, Fixed, In Review, Ready for QA, Verified, Closed, Reopened
    
    # Add assignment fields
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS reporter_id VARCHAR(20) REFERENCES users(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS assignee_id VARCHAR(20) REFERENCES users(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS qa_owner_id VARCHAR(20) REFERENCES users(id)")
    
    # Add reproduction path fields
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS reproduction_steps TEXT")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS expected_result TEXT")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS actual_result TEXT")
    
    # Add linked items fields
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS linked_task_id VARCHAR(20)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS linked_commit VARCHAR(255)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS linked_pr VARCHAR(255)")
    
    # Add component_attached_to field
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS component_attached_to VARCHAR(255)")
    
    # Add closed_at timestamp for tracking closure
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS closed_at TIMESTAMP WITH TIME ZONE")
    
    # Create indexes for all new columns
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_test_run ON bugs(test_run_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_test_case ON bugs(test_case_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_category ON bugs(category) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_severity ON bugs(severity) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_priority ON bugs(priority) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_reporter ON bugs(reporter_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_assignee ON bugs(assignee_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_qa_owner ON bugs(qa_owner_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_component ON bugs(component_attached_to) WHERE is_deleted = false")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_bugs_component")
    op.execute("DROP INDEX IF EXISTS idx_bugs_qa_owner")
    op.execute("DROP INDEX IF EXISTS idx_bugs_assignee")
    op.execute("DROP INDEX IF EXISTS idx_bugs_reporter")
    op.execute("DROP INDEX IF EXISTS idx_bugs_status")
    op.execute("DROP INDEX IF EXISTS idx_bugs_priority")
    op.execute("DROP INDEX IF EXISTS idx_bugs_severity")
    op.execute("DROP INDEX IF EXISTS idx_bugs_category")
    op.execute("DROP INDEX IF EXISTS idx_bugs_test_case")
    op.execute("DROP INDEX IF EXISTS idx_bugs_test_run")
    
    # Drop columns
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS closed_at")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS component_attached_to")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS linked_pr")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS linked_commit")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS linked_task_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS actual_result")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS expected_result")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS reproduction_steps")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS qa_owner_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS assignee_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS reporter_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS status")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS priority")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS severity")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS category")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS test_case_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS test_run_id")

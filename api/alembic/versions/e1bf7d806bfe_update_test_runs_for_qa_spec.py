"""update_test_runs_for_qa_spec

Revision ID: e1bf7d806bfe
Revises: 6728695f12f4
Create Date: 2025-11-16 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1bf7d806bfe'
down_revision: Union[str, Sequence[str], None] = '6728695f12f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update test_runs table to match QA spec requirements."""
    # Add hierarchy associations (nullable, only one should be set)
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS project_id VARCHAR(20) REFERENCES projects(id)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS usecase_id VARCHAR(20) REFERENCES usecases(id)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS user_story_id VARCHAR(20) REFERENCES user_stories(id)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS task_id VARCHAR(20) REFERENCES tasks(id)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS subtask_id VARCHAR(20) REFERENCES subtasks(id)")
    
    # Add new test run fields
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS purpose TEXT")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS short_description VARCHAR(500)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS long_description TEXT")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS component_attached_to VARCHAR(255)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS run_type VARCHAR(50) DEFAULT 'Misc'")
    
    # Rename metrics columns to match spec
    op.execute("ALTER TABLE test_runs RENAME COLUMN total_tests TO total_test_cases")
    op.execute("ALTER TABLE test_runs RENAME COLUMN passed_tests TO passed_test_cases")
    op.execute("ALTER TABLE test_runs RENAME COLUMN failed_tests TO failed_test_cases")
    op.execute("ALTER TABLE test_runs RENAME COLUMN blocked_tests TO blocked_test_cases")
    
    # Remove skipped_tests column (not in spec)
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS skipped_tests")
    
    # Remove sprint_id and release_version (not in spec)
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS sprint_id")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS release_version")
    
    # Add constraint to ensure only one hierarchy level is set
    op.execute("""
        ALTER TABLE test_runs ADD CONSTRAINT test_run_hierarchy_check CHECK (
            (project_id IS NOT NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NOT NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NOT NULL AND task_id IS NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NOT NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NOT NULL)
        )
    """)
    
    # Create indexes for hierarchy relationships
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_project ON test_runs(project_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_usecase ON test_runs(usecase_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_user_story ON test_runs(user_story_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_task ON test_runs(task_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_subtask ON test_runs(subtask_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_type ON test_runs(run_type) WHERE is_deleted = false")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_test_runs_type")
    op.execute("DROP INDEX IF EXISTS idx_test_runs_subtask")
    op.execute("DROP INDEX IF EXISTS idx_test_runs_task")
    op.execute("DROP INDEX IF EXISTS idx_test_runs_user_story")
    op.execute("DROP INDEX IF EXISTS idx_test_runs_usecase")
    op.execute("DROP INDEX IF EXISTS idx_test_runs_project")
    
    # Drop constraint
    op.execute("ALTER TABLE test_runs DROP CONSTRAINT IF EXISTS test_run_hierarchy_check")
    
    # Add back removed columns
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS sprint_id VARCHAR(50)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS release_version VARCHAR(50)")
    op.execute("ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS skipped_tests INTEGER DEFAULT 0")
    
    # Rename metrics columns back
    op.execute("ALTER TABLE test_runs RENAME COLUMN blocked_test_cases TO blocked_tests")
    op.execute("ALTER TABLE test_runs RENAME COLUMN failed_test_cases TO failed_tests")
    op.execute("ALTER TABLE test_runs RENAME COLUMN passed_test_cases TO passed_tests")
    op.execute("ALTER TABLE test_runs RENAME COLUMN total_test_cases TO total_tests")
    
    # Drop new columns
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS run_type")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS component_attached_to")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS long_description")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS short_description")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS purpose")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS subtask_id")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS task_id")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS user_story_id")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS usecase_id")
    op.execute("ALTER TABLE test_runs DROP COLUMN IF EXISTS project_id")

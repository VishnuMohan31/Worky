"""update_test_cases_for_qa_spec

Revision ID: 05fb4fcf5df1
Revises: e1bf7d806bfe
Create Date: 2025-11-16 16:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05fb4fcf5df1'
down_revision: Union[str, Sequence[str], None] = 'e1bf7d806bfe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update test_cases table to match QA spec requirements."""
    # Add test_run_id foreign key to link test cases to test runs
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS test_run_id VARCHAR(20) REFERENCES test_runs(id)")
    
    # Rename fields to match spec
    op.execute("ALTER TABLE test_cases RENAME COLUMN title TO test_case_name")
    op.execute("ALTER TABLE test_cases RENAME COLUMN description TO test_case_description")
    
    # Add new fields from spec
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS actual_result TEXT")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS inference TEXT")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS component_attached_to VARCHAR(255)")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS remarks TEXT")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS executed_by VARCHAR(20) REFERENCES users(id)")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS executed_at TIMESTAMP WITH TIME ZONE")
    
    # Update status values to match spec (Not Executed, Passed, Failed, Blocked, Skipped)
    # The existing status field will be updated, no need to recreate
    
    # Remove fields not in spec
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS preconditions")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS test_data")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS test_type")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS version")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS tags")
    
    # Drop old hierarchy constraint
    op.execute("ALTER TABLE test_cases DROP CONSTRAINT IF EXISTS test_case_hierarchy_check")
    
    # Remove hierarchy columns (test cases now belong to test runs, not directly to hierarchy)
    op.execute("DROP INDEX IF EXISTS idx_test_cases_project")
    op.execute("DROP INDEX IF EXISTS idx_test_cases_usecase")
    op.execute("DROP INDEX IF EXISTS idx_test_cases_user_story")
    op.execute("DROP INDEX IF EXISTS idx_test_cases_task")
    op.execute("DROP INDEX IF EXISTS idx_test_cases_type")
    
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS project_id")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS usecase_id")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS user_story_id")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS task_id")
    
    # Create index for test_run_id
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_test_run ON test_cases(test_run_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_component ON test_cases(component_attached_to) WHERE is_deleted = false")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new indexes
    op.execute("DROP INDEX IF EXISTS idx_test_cases_component")
    op.execute("DROP INDEX IF EXISTS idx_test_cases_test_run")
    
    # Add back hierarchy columns
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS project_id VARCHAR(20) REFERENCES projects(id)")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS usecase_id VARCHAR(20) REFERENCES usecases(id)")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS user_story_id VARCHAR(20) REFERENCES user_stories(id)")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS task_id VARCHAR(20) REFERENCES tasks(id)")
    
    # Add back removed columns BEFORE creating indexes on them
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS tags TEXT")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS test_type VARCHAR(50)")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS test_data TEXT")
    op.execute("ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS preconditions TEXT")
    
    # Now create indexes on existing columns
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_project ON test_cases(project_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_usecase ON test_cases(usecase_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_user_story ON test_cases(user_story_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_task ON test_cases(task_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_type ON test_cases(test_type) WHERE is_deleted = false")
    
    # Add back hierarchy constraint
    op.execute("""
        ALTER TABLE test_cases ADD CONSTRAINT test_case_hierarchy_check CHECK (
            (project_id IS NOT NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NOT NULL AND user_story_id IS NULL AND task_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NOT NULL AND task_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NOT NULL)
        )
    """)
    
    # Drop new columns
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS executed_at")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS executed_by")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS remarks")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS component_attached_to")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS inference")
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS actual_result")
    
    # Rename fields back
    op.execute("ALTER TABLE test_cases RENAME COLUMN test_case_description TO description")
    op.execute("ALTER TABLE test_cases RENAME COLUMN test_case_name TO title")
    
    # Drop test_run_id
    op.execute("ALTER TABLE test_cases DROP COLUMN IF EXISTS test_run_id")

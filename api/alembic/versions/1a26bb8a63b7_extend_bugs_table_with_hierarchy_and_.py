"""extend_bugs_table_with_hierarchy_and_new_fields

Revision ID: 1a26bb8a63b7
Revises: 71458e0c66fb
Create Date: 2025-11-15 17:59:17.816590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a26bb8a63b7'
down_revision: Union[str, Sequence[str], None] = '71458e0c66fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add hierarchy relationship columns (one at a time for asyncpg compatibility)
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS client_id VARCHAR(20) REFERENCES clients(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS program_id VARCHAR(20) REFERENCES programs(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS project_id VARCHAR(20) REFERENCES projects(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS usecase_id VARCHAR(20) REFERENCES usecases(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS user_story_id VARCHAR(20) REFERENCES user_stories(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS task_id VARCHAR(20) REFERENCES tasks(id)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS subtask_id VARCHAR(20) REFERENCES subtasks(id)")
    
    # Add bug type, resolution type, and version tracking fields
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS bug_type VARCHAR(50)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS resolution_type VARCHAR(50)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS found_in_version VARCHAR(50)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS fixed_in_version VARCHAR(50)")
    
    # Add environment fields (browser, OS, device_type)
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS browser VARCHAR(50)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS os VARCHAR(50)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS device_type VARCHAR(50)")
    
    # Add reopen_count and resolution_notes fields
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS reopen_count INTEGER DEFAULT 0")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS resolution_notes TEXT")
    
    # Create indexes for hierarchy relationships
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_client ON bugs(client_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_program ON bugs(program_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_project ON bugs(project_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_usecase ON bugs(usecase_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_user_story ON bugs(user_story_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_task ON bugs(task_id) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_subtask ON bugs(subtask_id) WHERE is_deleted = false")
    
    # Create indexes for bug_type and resolution_type
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_type ON bugs(bug_type) WHERE is_deleted = false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bugs_resolution ON bugs(resolution_type) WHERE is_deleted = false")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes (one at a time for asyncpg compatibility)
    op.execute("DROP INDEX IF EXISTS idx_bugs_resolution")
    op.execute("DROP INDEX IF EXISTS idx_bugs_type")
    op.execute("DROP INDEX IF EXISTS idx_bugs_subtask")
    op.execute("DROP INDEX IF EXISTS idx_bugs_task")
    op.execute("DROP INDEX IF EXISTS idx_bugs_user_story")
    op.execute("DROP INDEX IF EXISTS idx_bugs_usecase")
    op.execute("DROP INDEX IF EXISTS idx_bugs_project")
    op.execute("DROP INDEX IF EXISTS idx_bugs_program")
    op.execute("DROP INDEX IF EXISTS idx_bugs_client")
    
    # Drop columns
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS resolution_notes")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS reopen_count")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS device_type")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS os")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS browser")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS fixed_in_version")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS found_in_version")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS resolution_type")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS bug_type")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS subtask_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS task_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS user_story_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS usecase_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS project_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS program_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS client_id")

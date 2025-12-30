"""rename_task_name_to_title

Revision ID: 879f5093c2d4
Revises: 41ee2f43d014
Create Date: 2025-11-15 12:14:26.023999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '879f5093c2d4'
down_revision: Union[str, Sequence[str], None] = '41ee2f43d014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if 'name' column exists and rename it to 'title'
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='tasks' AND column_name='name'
            ) THEN
                ALTER TABLE tasks RENAME COLUMN name TO title;
            END IF;
        END $$;
    """)
    
    # Do the same for subtasks
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='subtasks' AND column_name='name'
            ) THEN
                ALTER TABLE subtasks RENAME COLUMN name TO title;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Rename back from title to name
    op.execute("ALTER TABLE tasks RENAME COLUMN title TO name")
    op.execute("ALTER TABLE subtasks RENAME COLUMN title TO name")

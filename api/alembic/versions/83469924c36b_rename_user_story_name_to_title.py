"""rename_user_story_name_to_title

Revision ID: 83469924c36b
Revises: 353a8e006cef
Create Date: 2025-11-15 12:57:33.731339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83469924c36b'
down_revision: Union[str, Sequence[str], None] = '353a8e006cef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename 'name' to 'title' in user_stories table if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='user_stories' AND column_name='name'
            ) THEN
                ALTER TABLE user_stories RENAME COLUMN name TO title;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE user_stories RENAME COLUMN title TO name")

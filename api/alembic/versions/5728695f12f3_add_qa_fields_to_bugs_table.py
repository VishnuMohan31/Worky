"""add_qa_fields_to_bugs_table

Revision ID: 5728695f12f3
Revises: 88a83cf77c44
Create Date: 2025-11-16 15:49:42.959231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5728695f12f3'
down_revision: Union[str, Sequence[str], None] = '88a83cf77c44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add QA-specific fields to bugs table."""
    # Add new QA fields to bugs table
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS description TEXT NOT NULL DEFAULT ''")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS environment VARCHAR(100)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS steps_to_reproduce TEXT")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS expected_behavior TEXT")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS actual_behavior TEXT")
    
    # Remove the default after adding the column
    op.execute("ALTER TABLE bugs ALTER COLUMN description DROP DEFAULT")
    
    # Drop old columns that are no longer needed
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS entity_type")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS entity_id")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS short_description")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS long_description")


def downgrade() -> None:
    """Downgrade schema."""
    # Add back old columns
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS entity_type VARCHAR(50)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS entity_id VARCHAR(20)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS short_description VARCHAR(500)")
    op.execute("ALTER TABLE bugs ADD COLUMN IF NOT EXISTS long_description TEXT")
    
    # Drop new QA fields
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS actual_behavior")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS expected_behavior")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS steps_to_reproduce")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS environment")
    op.execute("ALTER TABLE bugs DROP COLUMN IF EXISTS description")

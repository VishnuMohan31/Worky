"""add_is_deleted_to_bugs

Revision ID: 353a8e006cef
Revises: 879f5093c2d4
Create Date: 2025-11-15 12:36:16.588107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '353a8e006cef'
down_revision: Union[str, Sequence[str], None] = '879f5093c2d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add columns only if they don't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='bugs' AND column_name='is_deleted'
            ) THEN
                ALTER TABLE bugs ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL;
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='bugs' AND column_name='created_by'
            ) THEN
                ALTER TABLE bugs ADD COLUMN created_by VARCHAR(255);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='bugs' AND column_name='updated_by'
            ) THEN
                ALTER TABLE bugs ADD COLUMN updated_by VARCHAR(255);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('bugs', 'updated_by')
    op.drop_column('bugs', 'created_by')
    op.drop_column('bugs', 'is_deleted')

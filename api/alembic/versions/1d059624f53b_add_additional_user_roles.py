"""add_additional_user_roles

Revision ID: 1d059624f53b
Revises: a1b2c3d4e5f6
Create Date: 2026-02-17 07:51:39.416198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d059624f53b'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing role check constraint
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check")
    
    # Add the new constraint with additional roles
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (
            role IN (
                'Admin',
                'Developer', 
                'Tester',
                'Architect',
                'Designer',
                'HR',
                'Product Manager',
                'DevOps',
                'Owner',
                'Contact Person'
            )
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new constraint
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check")
    
    # Restore the original constraint with only 5 roles
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (
            role IN ('Admin', 'Developer', 'Tester', 'Architect', 'Designer')
        )
    """)

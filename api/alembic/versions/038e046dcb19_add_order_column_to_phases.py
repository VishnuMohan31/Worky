"""add_order_column_to_phases

Revision ID: 038e046dcb19
Revises: ec2ba519236e
Create Date: 2025-11-28 19:11:22.503466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '038e046dcb19'
down_revision: Union[str, Sequence[str], None] = 'ec2ba519236e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add order column to phases table
    op.add_column('phases', sa.Column('order', sa.Integer(), nullable=False, server_default='0'))
    
    # Update existing phases with sequential order values
    op.execute("""
        UPDATE phases 
        SET "order" = subquery.row_num 
        FROM (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as row_num 
            FROM phases
        ) AS subquery 
        WHERE phases.id = subquery.id
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove order column from phases table
    op.drop_column('phases', 'order')

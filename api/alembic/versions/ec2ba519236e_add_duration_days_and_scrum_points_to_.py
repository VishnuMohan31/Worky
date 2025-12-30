"""add_duration_days_and_scrum_points_to_subtasks

Revision ID: ec2ba519236e
Revises: 5a4b98c711ca
Create Date: 2025-11-18 15:09:24.119177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec2ba519236e'
down_revision: Union[str, Sequence[str], None] = '5a4b98c711ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add duration_days column to subtasks table
    op.add_column('subtasks', sa.Column('duration_days', sa.Integer(), nullable=True))
    
    # Add scrum_points column to subtasks table
    op.add_column('subtasks', sa.Column('scrum_points', sa.Numeric(precision=5, scale=2), nullable=True))
    
    # Add comments for the new columns
    op.execute("""
        COMMENT ON COLUMN subtasks.duration_days IS 'Category: Dates & Timeline | Number of calendar days expected to complete the subtask';
    """)
    
    op.execute("""
        COMMENT ON COLUMN subtasks.scrum_points IS 'Category: Dates & Timeline | Story points assigned to subtask for agile estimation';
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the columns
    op.drop_column('subtasks', 'scrum_points')
    op.drop_column('subtasks', 'duration_days')

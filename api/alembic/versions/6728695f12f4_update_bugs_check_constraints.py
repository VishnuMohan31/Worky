"""update_bugs_check_constraints

Revision ID: 6728695f12f4
Revises: 5728695f12f3
Create Date: 2025-11-16 15:54:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6728695f12f4'
down_revision: Union[str, Sequence[str], None] = '5728695f12f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update bugs table check constraints to match new enum values."""
    # Drop old check constraints
    op.execute("ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_priority_check")
    op.execute("ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_severity_check")
    op.execute("ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_status_check")
    
    # Update existing data to match new format
    op.execute("UPDATE bugs SET priority = 'P0 (Critical)' WHERE priority = 'P0'")
    op.execute("UPDATE bugs SET priority = 'P1 (High)' WHERE priority = 'P1'")
    op.execute("UPDATE bugs SET priority = 'P2 (Medium)' WHERE priority = 'P2'")
    op.execute("UPDATE bugs SET priority = 'P3 (Low)' WHERE priority = 'P3'")
    
    op.execute("UPDATE bugs SET severity = 'Blocker' WHERE severity = 'Critical' AND severity NOT IN ('Blocker', 'Major', 'Minor', 'Trivial')")
    op.execute("UPDATE bugs SET severity = 'Critical' WHERE severity = 'High'")
    op.execute("UPDATE bugs SET severity = 'Major' WHERE severity = 'Medium'")
    op.execute("UPDATE bugs SET severity = 'Minor' WHERE severity = 'Low'")
    
    op.execute("UPDATE bugs SET status = 'Open' WHERE status = 'Assigned'")
    
    # Add new check constraints with updated values
    op.execute("""
        ALTER TABLE bugs ADD CONSTRAINT bugs_priority_check 
        CHECK (priority IN ('P0 (Critical)', 'P1 (High)', 'P2 (Medium)', 'P3 (Low)', 'P4 (Trivial)'))
    """)
    
    op.execute("""
        ALTER TABLE bugs ADD CONSTRAINT bugs_severity_check 
        CHECK (severity IN ('Blocker', 'Critical', 'Major', 'Minor', 'Trivial'))
    """)
    
    op.execute("""
        ALTER TABLE bugs ADD CONSTRAINT bugs_status_check 
        CHECK (status IN ('New', 'Open', 'In Progress', 'Fixed', 'Ready for Testing', 'Retest', 'Verified', 'Closed', 'Reopened', 'Deferred', 'Rejected'))
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new check constraints
    op.execute("ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_priority_check")
    op.execute("ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_severity_check")
    op.execute("ALTER TABLE bugs DROP CONSTRAINT IF EXISTS bugs_status_check")
    
    # Add back old check constraints
    op.execute("""
        ALTER TABLE bugs ADD CONSTRAINT bugs_priority_check 
        CHECK (priority IN ('P0', 'P1', 'P2', 'P3'))
    """)
    
    op.execute("""
        ALTER TABLE bugs ADD CONSTRAINT bugs_severity_check 
        CHECK (severity IN ('Critical', 'High', 'Medium', 'Low'))
    """)
    
    op.execute("""
        ALTER TABLE bugs ADD CONSTRAINT bugs_status_check 
        CHECK (status IN ('New', 'Assigned', 'In Progress', 'Fixed', 'Verified', 'Closed', 'Reopened'))
    """)

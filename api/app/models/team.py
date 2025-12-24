"""
Team management models for the Worky API.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Team(Base):
    """Team model for project-based team management."""
    __tablename__ = "teams"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    project_id = Column(String(50), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(50), ForeignKey("users.id"))
    updated_by = Column(String(50), ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    # Indexes
    __table_args__ = (
        Index('idx_teams_project', 'project_id'),
        Index('idx_teams_active', 'is_active'),
    )

    def __repr__(self):
        return f"<Team(id='{self.id}', name='{self.name}', project_id='{self.project_id}')>"


class TeamMember(Base):
    """Team member model for user-team associations."""
    __tablename__ = "team_members"

    id = Column(String(50), primary_key=True)
    team_id = Column(String(50), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(100), default="Member")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    created_by = Column(String(50), ForeignKey("users.id"))

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes and constraints
    __table_args__ = (
        Index('idx_team_members_team', 'team_id'),
        Index('idx_team_members_user', 'user_id'),
        Index('idx_team_members_active', 'is_active'),
        # Unique constraint to prevent duplicate memberships
        Index('idx_team_members_unique', 'team_id', 'user_id', unique=True),
    )

    def __repr__(self):
        return f"<TeamMember(team_id='{self.team_id}', user_id='{self.user_id}', role='{self.role}')>"


class Assignment(Base):
    """Assignment model for entity-user assignments."""
    __tablename__ = "assignments"

    id = Column(String(50), primary_key=True)
    entity_type = Column(String(50), nullable=False)  # 'client', 'program', 'project', etc.
    entity_id = Column(String(50), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assignment_type = Column(String(50), nullable=False)  # 'owner', 'contact_person', 'developer'
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    created_by = Column(String(50), ForeignKey("users.id"))
    updated_by = Column(String(50), ForeignKey("users.id"))

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    history = relationship("AssignmentHistory", back_populates="assignment", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_assignments_entity', 'entity_type', 'entity_id'),
        Index('idx_assignments_user', 'user_id'),
        Index('idx_assignments_type', 'assignment_type'),
        # Unique constraint for owner/contact_person assignments - temporarily disabled
        # Index('idx_assignments_unique_owner', 'entity_type', 'entity_id', 'assignment_type', 
        #       unique=True, postgresql_where=(assignment_type.in_(['owner', 'contact_person']) & (is_active == True))),
    )

    def __repr__(self):
        return f"<Assignment(entity_type='{self.entity_type}', entity_id='{self.entity_id}', user_id='{self.user_id}', type='{self.assignment_type}')>"


class AssignmentHistory(Base):
    """Assignment history model for audit trail."""
    __tablename__ = "assignment_history"

    id = Column(String(50), primary_key=True)
    assignment_id = Column(String(50), ForeignKey("assignments.id", ondelete="SET NULL"))
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    assignment_type = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)  # 'assigned', 'unassigned', 'updated'
    previous_user_id = Column(String(50), ForeignKey("users.id"))  # For reassignments
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(50), ForeignKey("users.id"))

    # Relationships
    assignment = relationship("Assignment", back_populates="history")
    user = relationship("User", foreign_keys=[user_id])
    previous_user = relationship("User", foreign_keys=[previous_user_id])
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes
    __table_args__ = (
        Index('idx_assignment_history_entity', 'entity_type', 'entity_id'),
        Index('idx_assignment_history_user', 'user_id'),
        Index('idx_assignment_history_date', 'created_at'),
    )

    def __repr__(self):
        return f"<AssignmentHistory(entity_type='{self.entity_type}', entity_id='{self.entity_id}', action='{self.action}')>"
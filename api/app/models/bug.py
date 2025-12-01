from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Bug(Base):
    __tablename__ = "bugs"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('BUG', 'bugs_id_seq')"))
    
    # Link to test run and test case (for bugs from test failures)
    test_run_id = Column(String(20), ForeignKey("test_runs.id"))
    test_case_id = Column(String(20), ForeignKey("test_cases.id"))
    
    # Hierarchy relationship columns (for bugs created directly, not from test cases)
    client_id = Column(String(20), ForeignKey("clients.id"))
    program_id = Column(String(20), ForeignKey("programs.id"))
    project_id = Column(String(20), ForeignKey("projects.id"))
    usecase_id = Column(String(20), ForeignKey("usecases.id"))
    user_story_id = Column(String(20), ForeignKey("user_stories.id"))
    task_id = Column(String(20), ForeignKey("tasks.id"))
    subtask_id = Column(String(20), ForeignKey("subtasks.id"))
    
    # Basic bug fields
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Bug categorization (following industry standards)
    category = Column(String(50))  # UI, Backend, Database, Integration, Performance, Security, Environment
    severity = Column(String(50))  # Critical, High, Medium, Low (Impact on system)
    priority = Column(String(50))  # P1, P2, P3, P4 (How soon it must be fixed)
    
    # Bug status workflow
    status = Column(String(50), default="New")  # New, Open, In Progress, Fixed, In Review, Ready for QA, Verified, Closed, Reopened
    
    # Assignments
    reporter_id = Column(String(20), ForeignKey("users.id"))  # Who reported the bug
    assignee_id = Column(String(20), ForeignKey("users.id"))  # Developer assigned
    qa_owner_id = Column(String(20), ForeignKey("users.id"))  # QA owner
    
    # Reproduction path
    reproduction_steps = Column(Text)  # Steps to reproduce
    expected_result = Column(Text)  # What should happen
    actual_result = Column(Text)  # What actually happens
    
    # Linked items
    linked_task_id = Column(String(20))  # Link to task/user story
    linked_commit = Column(String(255))  # Git commit hash
    linked_pr = Column(String(255))  # Pull request URL
    
    # Additional fields
    component_attached_to = Column(String(255))  # Component/module affected
    environment = Column(String(255))  # Environment where bug found
    reopen_count = Column(Integer, default=0)
    resolution_notes = Column(Text)
    
    # Legacy fields (kept for backward compatibility)
    reported_by = Column(String(20), ForeignKey("users.id"))  # Deprecated, use reporter_id
    assigned_to = Column(String(20), ForeignKey("users.id"))  # Deprecated, use assignee_id
    bug_type = Column(String(50))  # Deprecated, use category
    resolution_type = Column(String(50))
    found_in_version = Column(String(50))
    fixed_in_version = Column(String(50))
    browser = Column(String(50))
    os = Column(String(50))
    device_type = Column(String(50))
    steps_to_reproduce = Column(Text)  # Deprecated, use reproduction_steps
    expected_behavior = Column(Text)  # Deprecated, use expected_result
    actual_behavior = Column(Text)  # Deprecated, use actual_result
    
    # Audit fields
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    # Relationships
    test_run = relationship("TestRun", foreign_keys=[test_run_id])
    test_case = relationship("TestCase", foreign_keys=[test_case_id])
    client = relationship("Client", foreign_keys=[client_id])
    program = relationship("Program", foreign_keys=[program_id])
    project = relationship("Project", foreign_keys=[project_id])
    usecase = relationship("Usecase", foreign_keys=[usecase_id])
    user_story = relationship("UserStory", foreign_keys=[user_story_id])
    task = relationship("Task", foreign_keys=[task_id])
    subtask = relationship("Subtask", foreign_keys=[subtask_id])
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    qa_owner = relationship("User", foreign_keys=[qa_owner_id])
    # Legacy relationships
    legacy_reporter = relationship("User", back_populates="reported_bugs", foreign_keys=[reported_by])
    legacy_assignee = relationship("User", foreign_keys=[assigned_to])
    comments = relationship("BugComment", back_populates="bug", cascade="all, delete-orphan")
    attachments = relationship("BugAttachment", back_populates="bug", cascade="all, delete-orphan")
    status_history = relationship("BugStatusHistory", back_populates="bug", cascade="all, delete-orphan")
    linked_test_cases = relationship("TestCaseBug", back_populates="bug", cascade="all, delete-orphan")
    
    @validates('category')
    def validate_category(self, key, value):
        """Validate category against allowed values"""
        if value is None:
            return value
        allowed_categories = ["UI", "Backend", "Database", "Integration", "Performance", "Security", "Environment"]
        if value not in allowed_categories:
            raise ValueError(f"category must be one of {allowed_categories}")
        return value
    
    @validates('severity')
    def validate_severity(self, key, value):
        """Validate severity against allowed values"""
        if value is None:
            return value
        allowed_severities = ["Critical", "High", "Medium", "Low"]
        if value not in allowed_severities:
            raise ValueError(f"severity must be one of {allowed_severities}")
        return value
    
    @validates('priority')
    def validate_priority(self, key, value):
        """Validate priority against allowed values"""
        if value is None:
            return value
        allowed_priorities = ["P1", "P2", "P3", "P4"]
        if value not in allowed_priorities:
            raise ValueError(f"priority must be one of {allowed_priorities}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate status against allowed values"""
        allowed_statuses = [
            "New", "Open", "In Progress", "Fixed", "In Review", 
            "Ready for QA", "Verified", "Closed", "Reopened"
        ]
        if value not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return value

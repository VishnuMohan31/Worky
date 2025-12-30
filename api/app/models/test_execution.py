from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean, CheckConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class TestRun(Base):
    """Test run for grouping test cases - can be attached to any hierarchy level"""
    __tablename__ = "test_runs"
    
    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    
    # Hierarchy associations (nullable, only one should be set)
    project_id = Column(String(20), ForeignKey("projects.id"), nullable=True)
    usecase_id = Column(String(20), ForeignKey("usecases.id"), nullable=True)
    user_story_id = Column(String(20), ForeignKey("user_stories.id"), nullable=True)
    task_id = Column(String(20), ForeignKey("tasks.id"), nullable=True)
    subtask_id = Column(String(20), ForeignKey("subtasks.id"), nullable=True)
    
    # Test run details
    name = Column(String(255), nullable=False)
    purpose = Column(Text)
    short_description = Column(String(500))
    long_description = Column(Text)
    component_attached_to = Column(String(255))  # e.g., "Login Module", "Payment Screen"
    
    # Classification
    run_type = Column(String(50), default='Misc')  # Misc, One-Timer
    status = Column(String(50), default='In Progress')  # In Progress, Completed, Aborted
    
    # Dates
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Metrics (calculated)
    total_test_cases = Column(Integer, default=0)
    passed_test_cases = Column(Integer, default=0)
    failed_test_cases = Column(Integer, default=0)
    blocked_test_cases = Column(Integer, default=0)
    
    # Audit fields
    created_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    updated_by = Column(String(20), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    usecase = relationship("Usecase", foreign_keys=[usecase_id])
    user_story = relationship("UserStory", foreign_keys=[user_story_id])
    task = relationship("Task", foreign_keys=[task_id])
    subtask = relationship("Subtask", foreign_keys=[subtask_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    test_cases = relationship("TestCase", back_populates="test_run", cascade="all, delete-orphan")
    executions = relationship("TestExecution", back_populates="test_run", cascade="all, delete-orphan")
    
    # Constraint to ensure only one hierarchy level is set
    __table_args__ = (
        CheckConstraint(
            """
            (project_id IS NOT NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NOT NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NOT NULL AND task_id IS NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NOT NULL AND subtask_id IS NULL) OR
            (project_id IS NULL AND usecase_id IS NULL AND user_story_id IS NULL AND task_id IS NULL AND subtask_id IS NOT NULL)
            """,
            name="test_run_hierarchy_check"
        ),
    )
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate status against allowed values"""
        allowed_statuses = ["In Progress", "Completed", "Aborted"]
        if value not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return value
    
    @validates('run_type')
    def validate_run_type(self, key, value):
        """Validate run type against allowed values"""
        allowed_types = ["Misc", "One-Timer"]
        if value not in allowed_types:
            raise ValueError(f"run_type must be one of {allowed_types}")
        return value


class TestExecution(Base):
    """Test execution record for a test case"""
    __tablename__ = "test_executions"
    
    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    test_case_id = Column(String(20), ForeignKey("test_cases.id"), nullable=False)
    test_run_id = Column(String(20), ForeignKey("test_runs.id"))  # Optional grouping
    
    # Execution details
    executed_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    execution_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    execution_status = Column(String(50), nullable=False)  # Passed, Failed, Blocked, Skipped, Not Applicable
    actual_result = Column(Text)
    execution_notes = Column(Text)
    
    # Environment
    environment = Column(String(100))  # e.g., "Chrome 120, Windows 11"
    browser = Column(String(50))
    os = Column(String(50))
    device_type = Column(String(50))
    
    # Attachments
    screenshots = Column(Text)  # JSON array of file paths
    log_files = Column(Text)  # JSON array of file paths
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    test_case = relationship("TestCase", back_populates="executions")
    test_run = relationship("TestRun", back_populates="executions")
    executor = relationship("User", foreign_keys=[executed_by])
    
    @validates('execution_status')
    def validate_execution_status(self, key, value):
        """Validate execution status against allowed values"""
        allowed_statuses = ["Passed", "Failed", "Blocked", "Skipped", "Not Applicable"]
        if value not in allowed_statuses:
            raise ValueError(f"execution_status must be one of {allowed_statuses}")
        return value

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean, CheckConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    
    # Belongs to a Test Run
    test_run_id = Column(String(20), ForeignKey("test_runs.id"), nullable=False)
    
    # Test case details
    test_case_name = Column(String(255), nullable=False)
    test_case_description = Column(Text)
    test_case_steps = Column(Text, nullable=False)  # JSON array of numbered steps
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text)  # Filled during execution
    inference = Column(Text)  # Conclusion/analysis after execution
    component_attached_to = Column(String(255))  # e.g., "Login Screen", "API Gateway"
    remarks = Column(Text)
    
    # Classification
    priority = Column(String(20))  # P0, P1, P2, P3
    status = Column(String(50), default='Not Executed')  # Not Executed, Passed, Failed, Blocked, Skipped
    
    # Execution tracking
    executed_by = Column(String(20), ForeignKey("users.id"))
    executed_at = Column(DateTime(timezone=True))
    
    # Audit fields
    created_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    updated_by = Column(String(20), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="test_cases")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    executor = relationship("User", foreign_keys=[executed_by])
    executions = relationship("TestExecution", back_populates="test_case", cascade="all, delete-orphan")
    comments = relationship("TestCaseComment", back_populates="test_case", cascade="all, delete-orphan")
    linked_bugs = relationship("TestCaseBug", back_populates="test_case", cascade="all, delete-orphan")
    
    @validates('priority')
    def validate_priority(self, key, value):
        """Validate priority against allowed values"""
        if value is None:
            return value
        allowed_priorities = ["P0", "P1", "P2", "P3"]
        if value not in allowed_priorities:
            raise ValueError(f"priority must be one of {allowed_priorities}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate status against allowed values"""
        allowed_statuses = ["Not Executed", "Passed", "Failed", "Blocked", "Skipped"]
        if value not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return value


class TestCaseBug(Base):
    """Junction table linking test cases to bugs"""
    __tablename__ = "test_case_bugs"
    
    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    test_case_id = Column(String(20), ForeignKey("test_cases.id"), nullable=False)
    bug_id = Column(String(20), ForeignKey("bugs.id"), nullable=False)
    test_execution_id = Column(String(20), ForeignKey("test_executions.id"))  # Which execution found the bug
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    test_case = relationship("TestCase", back_populates="linked_bugs")
    bug = relationship("Bug", back_populates="linked_test_cases")
    test_execution = relationship("TestExecution", foreign_keys=[test_execution_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        CheckConstraint(
            "test_case_id != bug_id",
            name="test_case_bug_different_entities"
        ),
    )

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class BugCategoryEnum(str, Enum):
    """Bug category enumeration"""
    UI = "UI"
    BACKEND = "Backend"
    DATABASE = "Database"
    INTEGRATION = "Integration"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    ENVIRONMENT = "Environment"


class BugSeverityEnum(str, Enum):
    """Bug severity enumeration"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class BugPriorityEnum(str, Enum):
    """Bug priority enumeration"""
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class BugStatusEnum(str, Enum):
    """Bug status enumeration"""
    NEW = "New"
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    FIXED = "Fixed"
    IN_REVIEW = "In Review"
    READY_FOR_QA = "Ready for QA"
    VERIFIED = "Verified"
    CLOSED = "Closed"
    REOPENED = "Reopened"


class BugTypeEnum(str, Enum):
    """Bug type enumeration (legacy)"""
    FUNCTIONAL = "Functional"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    UI_UX = "UI/UX"
    DATA = "Data"
    INTEGRATION = "Integration"
    CONFIGURATION = "Configuration"


class ResolutionTypeEnum(str, Enum):
    """Bug resolution type enumeration"""
    FIXED = "Fixed"
    DUPLICATE = "Duplicate"
    CANNOT_REPRODUCE = "Cannot Reproduce"
    WONT_FIX = "Won't Fix"
    BY_DESIGN = "By Design"
    DEFERRED = "Deferred"


class BugBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category: Optional[BugCategoryEnum] = None
    severity: Optional[BugSeverityEnum] = None
    priority: Optional[BugPriorityEnum] = None
    reproduction_steps: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    component_attached_to: Optional[str] = Field(None, max_length=255)
    environment: Optional[str] = Field(None, max_length=255)


class BugCreate(BugBase):
    # Link to test run and test case (for bugs from test failures)
    test_run_id: Optional[str] = None
    test_case_id: Optional[str] = None
    
    # Hierarchy associations (for bugs created directly)
    client_id: Optional[str] = None
    program_id: Optional[str] = None
    project_id: Optional[str] = None
    usecase_id: Optional[str] = None
    user_story_id: Optional[str] = None
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None
    
    # Assignments
    reporter_id: Optional[str] = None
    assignee_id: Optional[str] = None
    qa_owner_id: Optional[str] = None
    
    # Linked items
    linked_task_id: Optional[str] = None
    linked_commit: Optional[str] = Field(None, max_length=255)
    linked_pr: Optional[str] = Field(None, max_length=255)


class BugUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[BugCategoryEnum] = None
    severity: Optional[BugSeverityEnum] = None
    priority: Optional[BugPriorityEnum] = None
    status: Optional[BugStatusEnum] = None
    reproduction_steps: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    component_attached_to: Optional[str] = Field(None, max_length=255)
    environment: Optional[str] = Field(None, max_length=255)
    assignee_id: Optional[str] = None
    qa_owner_id: Optional[str] = None
    linked_task_id: Optional[str] = None
    linked_commit: Optional[str] = Field(None, max_length=255)
    linked_pr: Optional[str] = Field(None, max_length=255)
    resolution_notes: Optional[str] = None


class BugStatusUpdate(BaseModel):
    """Schema for updating bug status"""
    status: BugStatusEnum
    resolution_type: Optional[ResolutionTypeEnum] = None
    resolution_notes: Optional[str] = None


class BugResponse(BugBase):
    id: str
    
    # Link to test run and test case
    test_run_id: Optional[str] = None
    test_case_id: Optional[str] = None
    
    # Hierarchy associations
    client_id: Optional[str] = None
    program_id: Optional[str] = None
    project_id: Optional[str] = None
    usecase_id: Optional[str] = None
    user_story_id: Optional[str] = None
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None
    
    # Status and assignments
    status: BugStatusEnum
    reporter_id: Optional[str] = None
    assignee_id: Optional[str] = None
    qa_owner_id: Optional[str] = None
    
    # Linked items
    linked_task_id: Optional[str] = None
    linked_commit: Optional[str] = None
    linked_pr: Optional[str] = None
    
    # Additional fields
    resolution_notes: Optional[str] = None
    reopen_count: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    
    # Optional: Include hierarchy path for display
    hierarchy_path: Optional[str] = None
    
    # Optional: Include test run/test case info
    test_run_name: Optional[str] = None
    test_case_name: Optional[str] = None
    
    # Optional: Include age in days
    age_days: Optional[int] = None

    class Config:
        from_attributes = True


class BugList(BaseModel):
    bugs: List[BugResponse]
    total: int
    page: int = 1
    page_size: int = 50
    has_more: bool = False

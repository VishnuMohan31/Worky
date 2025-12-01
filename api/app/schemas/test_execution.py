from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ExecutionStatusEnum(str, Enum):
    """Test execution status enumeration"""
    PASSED = "Passed"
    FAILED = "Failed"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"
    NOT_APPLICABLE = "Not Applicable"


class TestRunStatusEnum(str, Enum):
    """Test run status enumeration"""
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ABORTED = "Aborted"


class TestRunTypeEnum(str, Enum):
    """Test run type enumeration"""
    MISC = "Misc"
    ONE_TIMER = "One-Timer"


# Test Execution Schemas
class TestExecutionBase(BaseModel):
    """Base schema for test execution"""
    execution_status: ExecutionStatusEnum
    actual_result: Optional[str] = None
    execution_notes: Optional[str] = None
    environment: Optional[str] = Field(None, max_length=100)
    browser: Optional[str] = Field(None, max_length=50)
    os: Optional[str] = Field(None, max_length=50)
    device_type: Optional[str] = Field(None, max_length=50)
    screenshots: Optional[str] = Field(None, description="JSON array of file paths")
    log_files: Optional[str] = Field(None, description="JSON array of file paths")


class TestExecutionCreate(TestExecutionBase):
    """Schema for creating a test execution"""
    test_case_id: str
    test_run_id: Optional[str] = None
    execution_date: Optional[datetime] = None


class TestExecutionResponse(TestExecutionBase):
    """Schema for test execution response"""
    id: str
    test_case_id: str
    test_run_id: Optional[str] = None
    executed_by: str
    execution_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestExecutionList(BaseModel):
    """Schema for paginated test execution list"""
    executions: List[TestExecutionResponse]
    total: int
    page: int = 1
    page_size: int = 50


# Test Run Schemas
class TestRunBase(BaseModel):
    """Base schema for test run"""
    name: str = Field(..., min_length=1, max_length=255)
    purpose: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    long_description: Optional[str] = None
    component_attached_to: Optional[str] = Field(None, max_length=255)
    run_type: Optional[TestRunTypeEnum] = TestRunTypeEnum.MISC
    status: Optional[TestRunStatusEnum] = TestRunStatusEnum.IN_PROGRESS


class TestRunCreate(TestRunBase):
    """Schema for creating a test run"""
    # Hierarchy association (exactly one must be set)
    project_id: Optional[str] = None
    usecase_id: Optional[str] = None
    user_story_id: Optional[str] = None
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None
    
    start_date: Optional[datetime] = None
    
    @validator('project_id', 'usecase_id', 'user_story_id', 'task_id', 'subtask_id')
    def validate_hierarchy(cls, v, values):
        """Ensure exactly one hierarchy level is set"""
        hierarchy_fields = ['project_id', 'usecase_id', 'user_story_id', 'task_id', 'subtask_id']
        # Count how many hierarchy fields are set
        set_count = sum(1 for field in hierarchy_fields if values.get(field))
        # Add 1 if current field has value
        if v:
            set_count += 1
        
        # After all fields are validated, exactly one should be set
        # This check happens on the last field
        if 'subtask_id' in values or v is not None:
            if set_count != 1:
                raise ValueError("Exactly one hierarchy level (project_id, usecase_id, user_story_id, task_id, or subtask_id) must be set")
        
        return v


class TestRunUpdate(BaseModel):
    """Schema for updating a test run"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    purpose: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    long_description: Optional[str] = None
    component_attached_to: Optional[str] = Field(None, max_length=255)
    run_type: Optional[TestRunTypeEnum] = None
    status: Optional[TestRunStatusEnum] = None
    end_date: Optional[datetime] = None


class TestRunResponse(TestRunBase):
    """Schema for test run response"""
    id: str
    project_id: Optional[str] = None
    usecase_id: Optional[str] = None
    user_story_id: Optional[str] = None
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_test_cases: int = 0
    passed_test_cases: int = 0
    failed_test_cases: int = 0
    blocked_test_cases: int = 0
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    # Calculated fields
    pass_rate: Optional[float] = None
    completion_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True


class TestRunList(BaseModel):
    """Schema for paginated test run list"""
    test_runs: List[TestRunResponse]
    total: int
    page: int = 1
    page_size: int = 50

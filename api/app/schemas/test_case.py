from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TestCasePriorityEnum(str, Enum):
    """Test case priority enumeration"""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TestCaseStatusEnum(str, Enum):
    """Test case status enumeration"""
    NOT_EXECUTED = "Not Executed"
    PASSED = "Passed"
    FAILED = "Failed"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"


class TestCaseBase(BaseModel):
    """Base schema for test case"""
    test_case_name: str = Field(..., min_length=1, max_length=255)
    test_case_description: Optional[str] = None
    test_case_steps: str = Field(..., min_length=1, description="JSON array of numbered steps")
    expected_result: str = Field(..., min_length=1)
    component_attached_to: Optional[str] = Field(None, max_length=255)
    remarks: Optional[str] = None
    priority: Optional[TestCasePriorityEnum] = None
    status: Optional[TestCaseStatusEnum] = TestCaseStatusEnum.NOT_EXECUTED


class TestCaseCreate(TestCaseBase):
    """Schema for creating a test case"""
    test_run_id: str = Field(..., description="Test run this test case belongs to")


class TestCaseUpdate(BaseModel):
    """Schema for updating a test case"""
    test_case_name: Optional[str] = Field(None, min_length=1, max_length=255)
    test_case_description: Optional[str] = None
    test_case_steps: Optional[str] = Field(None, description="JSON array of numbered steps")
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    inference: Optional[str] = None
    component_attached_to: Optional[str] = Field(None, max_length=255)
    remarks: Optional[str] = None
    priority: Optional[TestCasePriorityEnum] = None
    status: Optional[TestCaseStatusEnum] = None


class TestCaseResponse(TestCaseBase):
    """Schema for test case response"""
    id: str
    test_run_id: str
    actual_result: Optional[str] = None
    inference: Optional[str] = None
    executed_by: Optional[str] = None
    executed_at: Optional[datetime] = None
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class TestCaseExecute(BaseModel):
    """Schema for executing a test case"""
    actual_result: str = Field(..., min_length=1, description="Actual result from test execution")
    inference: str = Field(..., min_length=1, description="Inference/conclusion from execution")
    status: TestCaseStatusEnum = Field(..., description="Execution status (Passed, Failed, Blocked, Skipped)")
    remarks: Optional[str] = Field(None, description="Additional remarks or notes")


class TestCaseList(BaseModel):
    """Schema for paginated test case list"""
    test_cases: List[TestCaseResponse]
    total: int
    page: int = 1
    page_size: int = 50
    
    class Config:
        from_attributes = True

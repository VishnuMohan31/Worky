from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class BugBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    severity: str = Field(..., description="Critical, High, Medium, Low")
    priority: str = Field(..., description="Urgent, High, Medium, Low")
    environment: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None


class BugCreate(BugBase):
    user_story_id: Optional[str] = None
    task_id: Optional[str] = None
    assigned_to: Optional[str] = None


class BugUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    environment: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None


class BugResponse(BugBase):
    id: str
    user_story_id: Optional[str] = None
    task_id: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    reported_by: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BugList(BaseModel):
    bugs: List[BugResponse]
    total: int
    page: int
    page_size: int

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class TaskBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    status: Optional[str] = "To Do"
    priority: Optional[str] = "Medium"
    estimated_hours: Optional[Decimal] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    user_story_id: str
    phase_id: Optional[str] = None
    assigned_to: Optional[str] = None
    sprint_id: Optional[str] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    phase_id: Optional[str] = None
    assigned_to: Optional[str] = None
    sprint_id: Optional[str] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class TaskResponse(TaskBase):
    id: str
    user_story_id: str
    phase_id: Optional[str] = None
    assigned_to: Optional[str] = None
    sprint_id: Optional[str] = None
    actual_hours: Optional[Decimal] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

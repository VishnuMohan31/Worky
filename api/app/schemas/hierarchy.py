"""
Hierarchy entity schemas for the Worky API.
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


# Program Schemas
class ProgramBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "Planning"


class ProgramCreate(ProgramBase):
    client_id: str


class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class ProgramResponse(ProgramBase):
    id: str
    client_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Usecase Schemas
class UsecaseBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    priority: Optional[str] = "Medium"
    status: Optional[str] = "Draft"


class UsecaseCreate(UsecaseBase):
    project_id: str


class UsecaseUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class UsecaseResponse(UsecaseBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User Story Schemas
class UserStoryBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    story_points: Optional[int] = None
    priority: Optional[str] = "Medium"
    status: Optional[str] = "Backlog"


class UserStoryCreate(UserStoryBase):
    usecase_id: str
    phase_id: str


class UserStoryUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    story_points: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    phase_id: Optional[str] = None


class UserStoryResponse(UserStoryBase):
    id: str
    usecase_id: str
    phase_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Subtask Schemas
class SubtaskBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    status: Optional[str] = "To Do"
    estimated_hours: Optional[Decimal] = None
    duration_days: Optional[int] = None
    scrum_points: Optional[Decimal] = None


class SubtaskCreate(SubtaskBase):
    task_id: str
    phase_id: Optional[str] = None
    assigned_to: Optional[str] = None


class SubtaskUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    status: Optional[str] = None
    phase_id: Optional[str] = None
    assigned_to: Optional[str] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    duration_days: Optional[int] = None
    scrum_points: Optional[Decimal] = None


class SubtaskResponse(SubtaskBase):
    id: str
    task_id: str
    phase_id: Optional[str] = None
    assigned_to: Optional[str] = None
    actual_hours: Optional[Decimal] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Phase Schemas
# Phase Schemas
class PhaseCreate(BaseModel):
    name: str
    description: Optional[str] = None  # Frontend sends 'description'
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    color: str = '#4A90E2'
    display_order: Optional[int] = None


class PhaseUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    color: Optional[str] = None
    display_order: Optional[int] = None


class PhaseResponse(BaseModel):
    id: str
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    color: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

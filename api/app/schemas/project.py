from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class ProjectBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "Planning"
    repository_url: Optional[str] = None
    sprint_length_weeks: Optional[str] = "2"  # "1" or "2"
    sprint_starting_day: Optional[str] = "Monday"  # Monday, Tuesday, Wednesday, etc.


class ProjectCreate(ProjectBase):
    program_id: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    repository_url: Optional[str] = None
    sprint_length_weeks: Optional[str] = None
    sprint_starting_day: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    program_id: str
    program_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

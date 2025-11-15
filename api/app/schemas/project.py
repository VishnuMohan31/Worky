from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "Planning"
    repository_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    program_id: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    repository_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    program_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

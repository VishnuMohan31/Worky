"""
Pydantic models for Excel data mapping.

These models define the structure of data extracted from Excel sheets
and provide validation before database insertion.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ImportResponse(BaseModel):
    """Response model for import operations."""
    success: bool
    message: str
    summary: dict[str, int] = Field(default_factory=dict)  # Entity type -> count
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0


class ProjectMapping(BaseModel):
    """Mapping model for Project entities from Excel."""
    excel_id: Optional[str] = None
    name: str
    description: str = ""
    client_name: str
    status: str = "Planning"
    priority: str = "Medium"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class UsecaseMapping(BaseModel):
    """Mapping model for Usecase entities from Excel."""
    excel_id: Optional[str] = None
    project_excel_id: str
    name: str
    description: str = ""
    status: str = "Draft"
    priority: str = "Medium"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class UserStoryMapping(BaseModel):
    """Mapping model for UserStory entities from Excel."""
    excel_id: Optional[str] = None
    usecase_excel_id: str
    title: str
    description: str = ""
    acceptance_criteria: str = ""
    status: str = "Backlog"
    priority: str = "Medium"
    owner: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TaskMapping(BaseModel):
    """Mapping model for Task entities from Excel."""
    excel_id: Optional[str] = None
    user_story_excel_id: str
    title: str
    description: str = ""
    status: str = "To Do"
    priority: str = "Medium"
    owner: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class SubtaskMapping(BaseModel):
    """Mapping model for Subtask entities from Excel."""
    excel_id: Optional[str] = None
    task_excel_id: str
    title: str
    description: str = ""
    status: str = "To Do"
    assigned_to: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None

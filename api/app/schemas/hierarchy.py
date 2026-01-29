"""
Hierarchy entity schemas for the Worky API.
"""
from pydantic import BaseModel, validator, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
import re


def parse_ddmmyyyy_date(date_input) -> date:
    """Parse DD/MM/YYYY string to date object, or return date object if already converted"""
    if not date_input:
        return None
    
    # If it's already a date object, return it
    if isinstance(date_input, date):
        return date_input
    
    # If it's not a string, convert to string first
    if not isinstance(date_input, str):
        date_str = str(date_input)
    else:
        date_str = date_input
    
    # Handle DD/MM/YYYY format
    if '/' in date_str:
        try:
            day, month, year = date_str.split('/')
            return date(int(year), int(month), int(day))
        except (ValueError, IndexError):
            raise ValueError(f"Invalid date format: {date_str}. Expected DD/MM/YYYY")
    
    # Handle YYYY-MM-DD format (for backward compatibility)
    if '-' in date_str and len(date_str) == 10:
        try:
            year, month, day = date_str.split('-')
            return date(int(year), int(month), int(day))
        except (ValueError, IndexError):
            raise ValueError(f"Invalid date format: {date_str}")
    
    raise ValueError(f"Invalid date format: {date_str}. Expected DD/MM/YYYY")


def format_date_to_ddmmyyyy(date_obj: date) -> str:
    """Format date object to DD/MM/YYYY string"""
    if not date_obj:
        return ""
    return f"{date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}"


class DDMMYYYYDate(str):
    """Custom date type that handles DD/MM/YYYY format"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not v:
            return None
        
        if isinstance(v, date):
            return format_date_to_ddmmyyyy(v)
        
        if isinstance(v, str):
            # Validate and convert to DD/MM/YYYY format
            date_obj = parse_ddmmyyyy_date(v)
            return format_date_to_ddmmyyyy(date_obj)
        
        raise ValueError('Invalid date format')
    
    def __repr__(self):
        return f'DDMMYYYYDate({super().__repr__()})'


# Program Schemas
class ProgramBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    end_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    status: Optional[str] = "Planning"

    @validator('start_date', 'end_date', pre=True)
    def validate_date_format(cls, v):
        if not v:
            return None
        
        if isinstance(v, date):
            return format_date_to_ddmmyyyy(v)
        
        if isinstance(v, str):
            date_obj = parse_ddmmyyyy_date(v)
            return format_date_to_ddmmyyyy(date_obj)
        
        return v


class ProgramCreate(ProgramBase):
    client_id: str

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date cannot be before start date')
        return v


class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    end_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    status: Optional[str] = None

    @validator('start_date', 'end_date', pre=True)
    def validate_date_format(cls, v):
        if not v:
            return None
        
        if isinstance(v, date):
            return format_date_to_ddmmyyyy(v)
        
        if isinstance(v, str):
            date_obj = parse_ddmmyyyy_date(v)
            return format_date_to_ddmmyyyy(date_obj)
        
        return v

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            # Parse both dates for comparison
            start_date_obj = parse_ddmmyyyy_date(values['start_date'])
            end_date_obj = parse_ddmmyyyy_date(v)
            if end_date_obj < start_date_obj:
                raise ValueError('End date cannot be before start date')
        return v


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
    status: Optional[str] = "Planning"  # Changed from "To Do" to "Planning"
    estimated_hours: Optional[Decimal] = None
    duration_days: Optional[int] = None
    scrum_points: Optional[Decimal] = None

    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return "Planning"  # Default to Planning
        
        valid_statuses = [
            "Planning", "In Progress", "Completed", "Blocked", "In Review", "On-Hold", "Canceled"
        ]
        
        if v not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Valid statuses are: {', '.join(valid_statuses)}")
        
        return v


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

    class Config:
        extra = "ignore"  # Ignore extra fields like story_points that don't belong to subtasks

    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        
        valid_statuses = [
            "Planning", "In Progress", "Completed", "Blocked", "In Review", "On-Hold", "Canceled"
        ]
        
        if v not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Valid statuses are: {', '.join(valid_statuses)}")
        
        return v

    @validator('estimated_hours', 'actual_hours', 'scrum_points')
    def validate_positive_numbers(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be non-negative')
        return v

    @validator('duration_days')
    def validate_duration_days(cls, v):
        if v is not None and v < 1:
            raise ValueError('Duration must be at least 1 day')
        return v


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

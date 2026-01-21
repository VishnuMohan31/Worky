from pydantic import BaseModel, validator, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


def parse_ddmmyyyy_date(date_str: str) -> date:
    """Parse DD/MM/YYYY string to date object"""
    if not date_str:
        return None
    
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


class TaskBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    status: Optional[str] = "Planning"
    priority: Optional[str] = "Medium"
    estimated_hours: Optional[Decimal] = None
    start_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    due_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")

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

    @validator('start_date', 'due_date', pre=True)
    def validate_date_format(cls, v):
        if not v:
            return None
        
        if isinstance(v, date):
            return format_date_to_ddmmyyyy(v)
        
        if isinstance(v, str):
            date_obj = parse_ddmmyyyy_date(v)
            return format_date_to_ddmmyyyy(date_obj)
        
        return v


class TaskCreate(TaskBase):
    user_story_id: str
    phase_id: Optional[str] = None
    assigned_to: Optional[str] = None
    sprint_id: Optional[str] = None

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            # Convert both dates to date objects for comparison
            try:
                start_date_obj = parse_ddmmyyyy_date(values['start_date'])
                due_date_obj = parse_ddmmyyyy_date(v)
                
                if due_date_obj < start_date_obj:
                    raise ValueError('Due date cannot be before start date')
            except ValueError as e:
                if "Due date cannot be before start date" in str(e):
                    raise e
                # If date parsing fails, let the date validator handle it
                pass
        return v


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
    start_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    due_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")

    @validator('start_date', 'due_date', pre=True)
    def validate_date_format(cls, v):
        if not v:
            return None
        
        if isinstance(v, date):
            return format_date_to_ddmmyyyy(v)
        
        if isinstance(v, str):
            date_obj = parse_ddmmyyyy_date(v)
            return format_date_to_ddmmyyyy(date_obj)
        
        return v

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            # Convert both dates to date objects for comparison
            try:
                start_date_obj = parse_ddmmyyyy_date(values['start_date'])
                due_date_obj = parse_ddmmyyyy_date(v)
                
                if due_date_obj < start_date_obj:
                    raise ValueError('Due date cannot be before start date')
            except ValueError as e:
                if "Due date cannot be before start date" in str(e):
                    raise e
                # If date parsing fails, let the date validator handle it
                pass
        return v


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

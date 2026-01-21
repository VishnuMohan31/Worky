from pydantic import BaseModel, validator, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime


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


class ProjectBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    end_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    status: Optional[str] = "Planning"
    repository_url: Optional[str] = None
    sprint_length_weeks: Optional[str] = "2"  # "1" or "2"
    sprint_starting_day: Optional[str] = "Monday"  # Monday, Tuesday, Wednesday, etc.

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


class ProjectCreate(ProjectBase):
    program_id: str

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            # Convert both dates to date objects for comparison
            try:
                start_date_obj = parse_ddmmyyyy_date(values['start_date'])
                end_date_obj = parse_ddmmyyyy_date(v)
                
                if end_date_obj < start_date_obj:
                    raise ValueError('End date cannot be before start date')
            except ValueError as e:
                if "End date cannot be before start date" in str(e):
                    raise e
                # If date parsing fails, let the date validator handle it
                pass
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    start_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    end_date: Optional[str] = Field(None, description="Date in DD/MM/YYYY format")
    status: Optional[str] = None
    repository_url: Optional[str] = None
    sprint_length_weeks: Optional[str] = None
    sprint_starting_day: Optional[str] = None

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
            # Convert both dates to date objects for comparison
            try:
                start_date_obj = parse_ddmmyyyy_date(values['start_date'])
                end_date_obj = parse_ddmmyyyy_date(v)
                
                if end_date_obj < start_date_obj:
                    raise ValueError('End date cannot be before start date')
            except ValueError as e:
                if "End date cannot be before start date" in str(e):
                    raise e
                # If date parsing fails, let the date validator handle it
                pass
        return v


class ProjectResponse(ProjectBase):
    id: str
    program_id: str
    program_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

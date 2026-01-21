"""
Client schemas for the Worky API.
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Client name is required')
        if len(v.strip()) < 2:
            raise ValueError('Client name must be at least 2 characters long')
        return v.strip()

    @validator('email')
    def validate_email(cls, v):
        if v and v.strip():
            # Basic email validation
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError('Invalid email format')
        return v.strip() if v else None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientList(BaseModel):
    clients: List[ClientResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

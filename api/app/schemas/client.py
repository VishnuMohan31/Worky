"""
Client schemas for the Worky API.
"""
from pydantic import BaseModel
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

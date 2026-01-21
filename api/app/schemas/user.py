from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str
    language: Optional[str] = "en"
    theme: Optional[str] = "snow"


class UserCreate(UserBase):
    password: str
    client_id: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    primary_role: Optional[str] = None
    secondary_roles: Optional[list] = None
    is_contact_person: Optional[bool] = None
    client_id: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    client_id: str
    primary_role: Optional[str] = None
    secondary_roles: Optional[list] = None
    is_contact_person: Optional[bool] = False
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
"""
Pydantic schemas for team management.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Team Schemas
class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_id: Optional[str] = None  # Nullable - team can be unassigned
    is_active: bool = True


class TeamCreate(TeamBase):
    project_id: str  # Required when creating a team


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    project_id: Optional[str] = None  # Can be set to a project ID or to empty string "" to clear
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Team Member Schemas
class TeamMemberBase(BaseModel):
    team_id: str
    user_id: str
    role: str = "Member"


class TeamMemberCreate(BaseModel):
    user_id: str
    role: str = "Member"


class TeamMemberUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(TeamMemberBase):
    id: str
    joined_at: datetime
    is_active: bool
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True


# Assignment Schemas
class AssignmentBase(BaseModel):
    entity_type: str = Field(..., pattern="^(client|program|project|usecase|userstory|task|subtask)$")
    entity_id: str
    user_id: str
    assignment_type: str = Field(..., pattern="^(owner|contact_person|developer|tester|designer|reviewer|lead)$")


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    user_id: Optional[str] = None
    assignment_type: Optional[str] = Field(None, pattern="^(owner|contact_person|developer|tester|designer|reviewer|lead)$")
    is_active: Optional[bool] = None


class AssignmentResponse(AssignmentBase):
    id: str
    assigned_at: datetime
    is_active: bool
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    entity_name: Optional[str] = None

    class Config:
        from_attributes = True


# Assignment History Schemas
class AssignmentHistoryResponse(BaseModel):
    id: str
    assignment_id: Optional[str] = None
    entity_type: str
    entity_id: str
    user_id: str
    assignment_type: str
    action: str
    previous_user_id: Optional[str] = None
    created_at: datetime
    user_name: Optional[str] = None
    previous_user_name: Optional[str] = None

    class Config:
        from_attributes = True


# Available Assignees Schema
class AvailableAssigneeResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    is_team_member: bool = False
    current_assignments: List[str] = []

    class Config:
        from_attributes = True


# Team with Members Schema
class TeamWithMembersResponse(TeamResponse):
    members: List[TeamMemberResponse] = []

    class Config:
        from_attributes = True


# Assignment Summary Schema
class AssignmentSummaryResponse(BaseModel):
    entity_type: str
    entity_id: str
    entity_name: Optional[str] = None
    assignments: List[AssignmentResponse] = []
    available_assignees: List[AvailableAssigneeResponse] = []

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import date, datetime
import re


# ============================================================================
# TODO Item Schemas
# ============================================================================

class LinkedTaskInfo(BaseModel):
    """Read-only summary information for linked tasks/subtasks"""
    id: str
    title: str
    status: str
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    parent_id: Optional[str] = None  # user_story_id for tasks, task_id for subtasks

    class Config:
        from_attributes = True


class TodoItemBase(BaseModel):
    """Base schema for TODO items with common fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Title of the TODO item")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed description")
    target_date: date = Field(..., description="Target date for the TODO item")
    visibility: Literal["public", "private"] = Field("private", description="Visibility setting")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class TodoItemCreate(TodoItemBase):
    """Schema for creating a new TODO item"""
    linked_entity_type: Optional[Literal["task", "subtask"]] = Field(
        None, 
        description="Type of linked entity"
    )
    linked_entity_id: Optional[str] = Field(
        None, 
        max_length=20,
        description="ID of the linked task or subtask"
    )

    @field_validator("linked_entity_id")
    @classmethod
    def validate_linked_entity(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that if linked_entity_id is provided, linked_entity_type must also be provided"""
        if v is not None:
            # Access linked_entity_type from the data being validated
            linked_entity_type = info.data.get("linked_entity_type")
            if not linked_entity_type:
                raise ValueError("linked_entity_type must be provided when linked_entity_id is set")
        return v


class TodoItemUpdate(BaseModel):
    """Schema for updating an existing TODO item"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    target_date: Optional[date] = None
    visibility: Optional[Literal["public", "private"]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty after stripping whitespace"""
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            return v.strip()
        return v


class TodoItemResponse(TodoItemBase):
    """Schema for TODO item responses"""
    id: str
    user_id: str
    linked_entity_type: Optional[Literal["task", "subtask"]] = None
    linked_entity_id: Optional[str] = None
    linked_entity_info: Optional[LinkedTaskInfo] = None
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodoItemList(BaseModel):
    """Schema for paginated list of TODO items"""
    items: List[TodoItemResponse]
    total: int


class MoveTodoItemRequest(BaseModel):
    """Schema for moving a TODO item to a different date"""
    target_date: date = Field(..., description="New target date for the TODO item")


class LinkTodoItemRequest(BaseModel):
    """Schema for linking a TODO item to a task or subtask"""
    entity_type: Literal["task", "subtask"] = Field(..., description="Type of entity to link")
    entity_id: str = Field(..., max_length=20, description="ID of the entity to link")


# ============================================================================
# ADHOC Note Schemas
# ============================================================================

class AdhocNoteBase(BaseModel):
    """Base schema for ADHOC notes with common fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Title of the note")
    content: Optional[str] = Field(None, description="Content of the note")
    color: str = Field("#FFEB3B", pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate color is a valid hex color code"""
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be a valid hex color code (e.g., #FFEB3B)")
        return v.upper()


class AdhocNoteCreate(AdhocNoteBase):
    """Schema for creating a new ADHOC note"""
    pass


class AdhocNoteUpdate(BaseModel):
    """Schema for updating an existing ADHOC note"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty after stripping whitespace"""
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            return v.strip()
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is a valid hex color code"""
        if v is not None:
            if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
                raise ValueError("Color must be a valid hex color code (e.g., #FFEB3B)")
            return v.upper()
        return v


class AdhocNoteResponse(AdhocNoteBase):
    """Schema for ADHOC note responses"""
    id: str
    user_id: str
    position: int
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdhocNoteList(BaseModel):
    """Schema for list of ADHOC notes"""
    notes: List[AdhocNoteResponse]
    total: int


class ReorderAdhocNoteRequest(BaseModel):
    """Schema for reordering an ADHOC note"""
    position: int = Field(..., ge=0, description="New position for the note (must be >= 0)")

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: int) -> int:
        """Validate position is non-negative"""
        if v < 0:
            raise ValueError("Position must be greater than or equal to 0")
        return v

"""
Dependency schemas for the Worky API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class DependencyType(str, Enum):
    """Dependency relationship types"""
    FINISH_TO_START = "finish_to_start"  # Task B starts when Task A finishes
    START_TO_START = "start_to_start"    # Task B starts when Task A starts
    FINISH_TO_FINISH = "finish_to_finish"  # Task B finishes when Task A finishes
    START_TO_FINISH = "start_to_finish"  # Task B finishes when Task A starts


class EntityType(str, Enum):
    """Valid entity types for dependencies"""
    PROGRAM = "Program"
    PROJECT = "Project"
    USECASE = "Usecase"
    USER_STORY = "UserStory"
    TASK = "Task"
    SUBTASK = "Subtask"


class DependencyBase(BaseModel):
    entity_type: EntityType
    entity_id: str
    depends_on_type: EntityType
    depends_on_id: str
    dependency_type: DependencyType = DependencyType.FINISH_TO_START


class DependencyCreate(DependencyBase):
    pass


class DependencyUpdate(BaseModel):
    dependency_type: Optional[DependencyType] = None


class DependencyResponse(DependencyBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DependencyWithDetails(DependencyResponse):
    """Dependency with entity details"""
    entity_name: Optional[str] = None
    depends_on_name: Optional[str] = None


class DependencyBulkCreate(BaseModel):
    """Create multiple dependencies at once"""
    dependencies: List[DependencyCreate]


class DependencyTreeNode(BaseModel):
    """Node in dependency tree/graph"""
    id: str
    entity_type: EntityType
    entity_id: str
    entity_name: str
    dependencies: List['DependencyTreeNode'] = []
    dependents: List['DependencyTreeNode'] = []


# Enable forward references
DependencyTreeNode.model_rebuild()

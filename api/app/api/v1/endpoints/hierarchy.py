"""
Hierarchy management endpoints for the Worky API.

This module provides unified endpoints for managing the hierarchical work breakdown structure,
including generic entity retrieval, statistics, and search functionality.

Requirements: 5.1, 5.2, 11.1, 11.2, 4.1, 4.2, 11.3, 12.1, 8.1, 8.2, 8.3, 25.1, 25.2, 25.3, 25.4, 2.1, 2.2, 2.3, 2.4, 6.1, 6.2, 6.3
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from uuid import UUID

from app.db.base import get_db
from app.models.client import Client
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.schemas.hierarchy import (
    ProgramCreate, ProgramUpdate, ProgramResponse,
    UsecaseCreate, UsecaseUpdate, UsecaseResponse,
    UserStoryCreate, UserStoryUpdate, UserStoryResponse,
    SubtaskCreate, SubtaskUpdate, SubtaskResponse
)
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger
from app.services.hierarchy_service import HierarchyService

router = APIRouter()
logger = StructuredLogger(__name__)


# ==================== HELPER FUNCTIONS ====================

async def _get_children_for_entity(
    db: AsyncSession,
    entity_type: str,
    entity_id: UUID
) -> List:
    """Get child entities for a given entity."""
    child_mapping = {
        'client': (Program, 'client_id'),
        'program': (Project, 'program_id'),
        'project': (Usecase, 'project_id'),
        'usecase': (UserStory, 'usecase_id'),
        'userstory': (Task, 'user_story_id'),
        'task': (Subtask, 'task_id')
    }
    
    if entity_type not in child_mapping:
        return []
    
    child_model, parent_field = child_mapping[entity_type]
    
    query = select(child_model).where(
        getattr(child_model, parent_field) == entity_id,
        child_model.is_deleted == False
    ).limit(100)  # Limit to prevent large responses
    
    result = await db.execute(query)
    return result.scalars().all()


def _entity_to_dict(entity) -> Optional[Dict[str, Any]]:
    """Convert SQLAlchemy entity to dictionary."""
    if not entity:
        return None
    
    result = {}
    for column in entity.__table__.columns:
        value = getattr(entity, column.name)
        # Convert UUID and datetime to string for JSON serialization
        if isinstance(value, UUID):
            value = str(value)
        elif hasattr(value, 'isoformat'):
            value = value.isoformat()
        result[column.name] = value
    
    return result


# ==================== GENERIC ENTITY RETRIEVAL ====================

@router.get("/{entity_type}/{entity_id}")
async def get_entity_with_context(
    entity_type: str = Path(..., description="Entity type (client, program, project, usecase, userstory, task, subtask)"),
    entity_id: str = Path(..., description="Entity ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get entity with parent, children, and breadcrumb context.
    
    This endpoint provides a unified way to retrieve any entity in the hierarchy
    along with its context (parent entity, child entities, and breadcrumb trail).
    
    Requirements: 5.1, 5.2, 11.1, 11.2
    
    Args:
        entity_type: Type of entity (client, program, project, usecase, userstory, task, subtask)
        entity_id: UUID of the entity
        
    Returns:
        Dictionary containing:
        - entity: The requested entity details
        - parent: Parent entity (null for Client)
        - children: List of child entities (empty for Subtask)
        - breadcrumb: Hierarchy path from Client to current entity
        
    Raises:
        400: Invalid entity type
        404: Entity not found
        403: Access denied (client-level isolation)
    """
    # Validate entity type
    valid_types = ['client', 'program', 'project', 'usecase', 'userstory', 'task', 'subtask']
    if entity_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_types)}"
        )
    
    service = HierarchyService(db)
    
    # Get entity and verify access
    await service._verify_entity_access(entity_type, entity_id, current_user)
    
    # Get entity details
    entity = await service._get_entity_by_type(entity_type.lower(), entity_id)
    
    if not entity:
        raise ResourceNotFoundException(entity_type, str(entity_id))
    
    # Get parent entity (null for Client)
    parent = None
    if entity_type.lower() != 'client':
        parent_info = service._get_parent_info(entity_type.lower(), entity)
        if parent_info:
            parent_type, parent_id = parent_info
            parent = await service._get_entity_by_type(parent_type, parent_id)
    
    # Get child entities (empty for Subtask)
    children = []
    if entity_type.lower() != 'subtask':
        children = await _get_children_for_entity(db, entity_type.lower(), entity_id)
    
    # Get breadcrumb trail
    breadcrumb = await service._get_breadcrumb_for_entity(entity_type.lower(), entity_id)
    
    # Log activity
    logger.log_activity(
        action="view_entity_with_context",
        entity_type=entity_type.lower(),
        entity_id=str(entity_id)
    )
    
    # Convert entities to dictionaries
    entity_dict = _entity_to_dict(entity)
    parent_dict = _entity_to_dict(parent) if parent else None
    children_dict = [_entity_to_dict(child) for child in children]
    
    return {
        "entity": entity_dict,
        "parent": parent_dict,
        "children": children_dict,
        "breadcrumb": breadcrumb
    }



# ==================== CLIENT ENDPOINTS ====================

@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List clients with pagination. Admin users see all clients, other users see only their assigned client."""
    query = select(Client).where(Client.is_deleted == False)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.where(Client.id == current_user.client_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    clients = result.scalars().all()
    
    logger.log_activity(action="list_clients", entity_type="client", entity_id="multiple")
    return [ClientResponse.from_orm(client) for client in clients]


@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Create a new client (Admin only)."""
    service = HierarchyService(db)
    client = await service.create_client(client_data, current_user)
    
    logger.log_activity(action="create_client", entity_type="client", entity_id=str(client.id), client_name=client.name)
    return ClientResponse.from_orm(client)


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Update a client (Admin only)."""
    service = HierarchyService(db)
    client = await service.update_client(client_id, client_data, current_user)
    
    logger.log_activity(action="update_client", entity_type="client", entity_id=str(client_id))
    return ClientResponse.from_orm(client)


# ==================== PROGRAM ENDPOINTS ====================

@router.get("/clients/{client_id}/programs", response_model=List[ProgramResponse])
async def list_programs_for_client(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List programs for a specific client."""
    service = HierarchyService(db)
    await service._get_and_verify_client_access(client_id, current_user)
    
    query = select(Program).where(Program.client_id == client_id, Program.is_deleted == False)
    if status_filter:
        query = query.where(Program.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    programs = result.scalars().all()
    
    logger.log_activity(action="list_programs", entity_type="program", entity_id="multiple", client_id=str(client_id))
    return [ProgramResponse.from_orm(prog) for prog in programs]


@router.post("/programs", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    program_data: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Create a new program (Admin, Architect)."""
    service = HierarchyService(db)
    program = await service.create_program(program_data, current_user)
    
    logger.log_activity(action="create_program", entity_type="program", entity_id=str(program.id), program_name=program.name)
    return ProgramResponse.from_orm(program)


@router.put("/programs/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: str,
    program_data: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Update a program (Admin, Architect)."""
    service = HierarchyService(db)
    program = await service.update_program(program_id, program_data, current_user)
    
    logger.log_activity(action="update_program", entity_type="program", entity_id=str(program_id))
    return ProgramResponse.from_orm(program)


@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Soft delete a program (Admin, Architect)."""
    service = HierarchyService(db)
    await service.delete_program(program_id, current_user)
    logger.log_activity(action="delete_program", entity_type="program", entity_id=str(program_id))


# ==================== PROJECT ENDPOINTS ====================

@router.get("/programs/{program_id}/projects", response_model=List[ProjectResponse])
async def list_projects_for_program(
    program_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List projects for a specific program."""
    from sqlalchemy.orm import selectinload
    
    service = HierarchyService(db)
    await service._get_and_verify_program_access(program_id, current_user)
    
    query = select(Project).options(selectinload(Project.program)).where(Project.program_id == program_id, Project.is_deleted == False)
    if status_filter:
        query = query.where(Project.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    logger.log_activity(action="list_projects", entity_type="project", entity_id="multiple", program_id=str(program_id))
    
    # Build response with program name
    response_list = []
    for proj in projects:
        proj_dict = ProjectResponse.from_orm(proj).dict()
        proj_dict["program_name"] = proj.program.name if proj.program else None
        response_list.append(ProjectResponse(**proj_dict))
    
    return response_list


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Create a new project (Admin, Architect)."""
    service = HierarchyService(db)
    project = await service.create_project(project_data, current_user)
    
    logger.log_activity(action="create_project", entity_type="project", entity_id=str(project.id), project_name=project.name)
    return ProjectResponse.from_orm(project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Update a project (Admin, Architect)."""
    service = HierarchyService(db)
    project = await service.update_project(project_id, project_data, current_user)
    
    logger.log_activity(action="update_project", entity_type="project", entity_id=str(project_id))
    return ProjectResponse.from_orm(project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Soft delete a project (Admin, Architect)."""
    service = HierarchyService(db)
    await service.delete_project(project_id, current_user)
    logger.log_activity(action="delete_project", entity_type="project", entity_id=str(project_id))



# ==================== USE CASE ENDPOINTS ====================

@router.get("/projects/{project_id}/usecases", response_model=List[UsecaseResponse])
async def list_usecases_for_project(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List use cases for a specific project."""
    service = HierarchyService(db)
    await service._get_and_verify_project_access(project_id, current_user)
    
    query = select(Usecase).where(Usecase.project_id == project_id, Usecase.is_deleted == False)
    if status_filter:
        query = query.where(Usecase.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    usecases = result.scalars().all()
    
    logger.log_activity(action="list_usecases", entity_type="usecase", entity_id="multiple", project_id=str(project_id))
    return [UsecaseResponse.from_orm(uc) for uc in usecases]


@router.post("/usecases", response_model=UsecaseResponse, status_code=status.HTTP_201_CREATED)
async def create_usecase(
    usecase_data: UsecaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Create a new use case (Admin, Architect, Designer)."""
    service = HierarchyService(db)
    usecase = await service.create_usecase(usecase_data, current_user)
    
    logger.log_activity(action="create_usecase", entity_type="usecase", entity_id=str(usecase.id), usecase_name=usecase.name)
    return UsecaseResponse.from_orm(usecase)


@router.put("/usecases/{usecase_id}", response_model=UsecaseResponse)
async def update_usecase(
    usecase_id: str,
    usecase_data: UsecaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Update a use case (Admin, Architect, Designer)."""
    service = HierarchyService(db)
    usecase = await service.update_usecase(usecase_id, usecase_data, current_user)
    
    logger.log_activity(action="update_usecase", entity_type="usecase", entity_id=str(usecase_id))
    return UsecaseResponse.from_orm(usecase)


@router.delete("/usecases/{usecase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usecase(
    usecase_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Soft delete a use case (Admin, Architect, Designer)."""
    service = HierarchyService(db)
    await service.delete_usecase(usecase_id, current_user)
    logger.log_activity(action="delete_usecase", entity_type="usecase", entity_id=str(usecase_id))


# ==================== USER STORY ENDPOINTS ====================

@router.get("/usecases/{usecase_id}/userstories", response_model=List[UserStoryResponse])
async def list_user_stories_for_usecase(
    usecase_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user stories for a specific use case."""
    service = HierarchyService(db)
    await service._get_and_verify_usecase_access(usecase_id, current_user)
    
    query = select(UserStory).where(UserStory.usecase_id == usecase_id, UserStory.is_deleted == False)
    if status_filter:
        query = query.where(UserStory.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    user_stories = result.scalars().all()
    
    logger.log_activity(action="list_user_stories", entity_type="userstory", entity_id="multiple", usecase_id=str(usecase_id))
    return [UserStoryResponse.from_orm(us) for us in user_stories]


@router.post("/userstories", response_model=UserStoryResponse, status_code=status.HTTP_201_CREATED)
async def create_user_story(
    story_data: UserStoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Create a new user story (Admin, Architect, Designer)."""
    service = HierarchyService(db)
    user_story = await service.create_user_story(story_data, current_user)
    
    logger.log_activity(action="create_user_story", entity_type="userstory", entity_id=str(user_story.id), user_story_title=user_story.title)
    return UserStoryResponse.from_orm(user_story)


@router.put("/userstories/{user_story_id}", response_model=UserStoryResponse)
async def update_user_story(
    user_story_id: str,
    story_data: UserStoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Update a user story (Admin, Architect, Designer)."""
    service = HierarchyService(db)
    user_story = await service.update_user_story(user_story_id, story_data, current_user)
    
    logger.log_activity(action="update_user_story", entity_type="userstory", entity_id=str(user_story_id))
    return UserStoryResponse.from_orm(user_story)


@router.delete("/userstories/{user_story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_story(
    user_story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Soft delete a user story (Admin, Architect, Designer)."""
    service = HierarchyService(db)
    await service.delete_user_story(user_story_id, current_user)
    logger.log_activity(action="delete_user_story", entity_type="userstory", entity_id=str(user_story_id))


# ==================== TASK ENDPOINTS ====================

@router.get("/userstories/{story_id}/tasks", response_model=List[TaskResponse])
async def list_tasks_for_user_story(
    story_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    phase_filter: Optional[UUID] = Query(None, alias="phase_id"),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tasks for a specific user story with phase and status filters."""
    service = HierarchyService(db)
    await service._get_and_verify_user_story_access(story_id, current_user)
    
    query = select(Task).where(Task.user_story_id == story_id, Task.is_deleted == False)
    if phase_filter:
        query = query.where(Task.phase_id == phase_filter)
    if status_filter:
        query = query.where(Task.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    logger.log_activity(action="list_tasks", entity_type="task", entity_id="multiple", user_story_id=str(story_id))
    return [TaskResponse.from_orm(task) for task in tasks]


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task with phase_id validation."""
    service = HierarchyService(db)
    task = await service.create_task(task_data, current_user)
    
    logger.log_activity(action="create_task", entity_type="task", entity_id=str(task.id), task_title=task.title)
    return TaskResponse.from_orm(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task."""
    service = HierarchyService(db)
    task = await service.update_task(task_id, task_data, current_user)
    
    logger.log_activity(action="update_task", entity_type="task", entity_id=str(task_id))
    return TaskResponse.from_orm(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a task."""
    service = HierarchyService(db)
    await service.delete_task(task_id, current_user)
    logger.log_activity(action="delete_task", entity_type="task", entity_id=str(task_id))


# ==================== SUBTASK ENDPOINTS ====================

@router.get("/tasks/{task_id}/subtasks", response_model=List[SubtaskResponse])
async def list_subtasks_for_task(
    task_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List subtasks for a specific task."""
    service = HierarchyService(db)
    await service._get_and_verify_task_access(task_id, current_user)
    
    query = select(Subtask).where(Subtask.task_id == task_id, Subtask.is_deleted == False).offset(skip).limit(limit)
    result = await db.execute(query)
    subtasks = result.scalars().all()
    
    logger.log_activity(action="list_subtasks", entity_type="subtask", entity_id="multiple", task_id=str(task_id))
    return [SubtaskResponse.from_orm(st) for st in subtasks]


@router.post("/subtasks", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    subtask_data: SubtaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new subtask with parent task validation. Validates that parent is a Task, not another Subtask."""
    service = HierarchyService(db)
    subtask = await service.create_subtask(subtask_data, current_user)
    
    logger.log_activity(action="create_subtask", entity_type="subtask", entity_id=str(subtask.id), subtask_title=subtask.title)
    return SubtaskResponse.from_orm(subtask)


@router.put("/subtasks/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    subtask_id: str,
    subtask_data: SubtaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a subtask."""
    service = HierarchyService(db)
    subtask = await service.update_subtask(subtask_id, subtask_data, current_user)
    
    logger.log_activity(action="update_subtask", entity_type="subtask", entity_id=str(subtask_id))
    return SubtaskResponse.from_orm(subtask)


@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    subtask_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a subtask."""
    service = HierarchyService(db)
    await service.delete_subtask(subtask_id, current_user)
    logger.log_activity(action="delete_subtask", entity_type="subtask", entity_id=str(subtask_id))


# ==================== STATISTICS ENDPOINT ====================

@router.get("/{entity_type}/{entity_id}/statistics")
async def get_entity_statistics(
    entity_type: str = Path(..., description="Entity type"),
    entity_id: str = Path(..., description="Entity ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for an entity including status counts, phase distribution, rollup counts, and completion percentage."""
    valid_types = ['client', 'program', 'project', 'usecase', 'userstory', 'task', 'subtask']
    if entity_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_types)}"
        )
    
    service = HierarchyService(db)
    statistics = await service.get_entity_statistics(entity_type.lower(), entity_id, current_user)
    
    logger.log_activity(action="view_entity_statistics", entity_type=entity_type.lower(), entity_id=str(entity_id))
    return statistics


# ==================== GLOBAL SEARCH ENDPOINT ====================

@router.get("/search")
async def search_entities(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    entity_types: Optional[List[str]] = Query(None, description="Entity types to search"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Results per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Global search across all entity types with hierarchy paths."""
    service = HierarchyService(db)
    results = await service.search_entities(query=q, entity_types=entity_types, current_user=current_user, page=page, page_size=page_size)
    
    logger.log_activity(action="search_entities", entity_type="multiple", entity_id="search", search_query=q)
    return results

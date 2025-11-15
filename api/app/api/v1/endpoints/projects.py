"""
Project endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.db.base import get_db
from app.models.hierarchy import Project, Program
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    program_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List projects with optional filters."""
    
    query = select(Project).join(Program).where(Project.is_deleted == False)
    
    # Apply filters
    if program_id:
        query = query.where(Project.program_id == program_id)
    if status:
        query = query.where(Project.status == status)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.where(Program.client_id == current_user.client_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    logger.log_activity(
        action="list_projects",
        entity_type="project",
        filters={"program_id": str(program_id) if program_id else None, "status": status}
    )
    
    return [ProjectResponse.from_orm(proj) for proj in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project by ID."""
    
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project", str(project_id))
    
    # Check access
    if current_user.role != "Admin":
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    logger.log_activity(
        action="view_project",
        entity_type="project",
        entity_id=str(project_id)
    )
    
    return ProjectResponse.from_orm(project)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Project Manager", "Architect"]))
):
    """Create a new project."""
    
    # Verify program exists
    program_result = await db.execute(
        select(Program).where(Program.id == project_data.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if not program:
        raise ResourceNotFoundException("Program", str(project_data.program_id))
    
    # Check access
    if current_user.role != "Admin" and program.client_id != current_user.client_id:
        raise AccessDeniedException()
    
    project = Project(
        **project_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    logger.log_activity(
        action="create_project",
        entity_type="project",
        entity_id=str(project.id),
        program_id=str(project.program_id),
        repository_url=project.repository_url
    )
    
    return ProjectResponse.from_orm(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Project Manager", "Architect"]))
):
    """Update a project."""
    
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project", str(project_id))
    
    # Check access
    if current_user.role != "Admin":
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    # Update fields
    for field, value in project_data.dict(exclude_unset=True).items():
        setattr(project, field, value)
    
    project.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(project)
    
    logger.log_activity(
        action="update_project",
        entity_type="project",
        entity_id=str(project_id),
        repository_url=project.repository_url
    )
    
    return ProjectResponse.from_orm(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Soft delete a project."""
    
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project", str(project_id))
    
    # Check access
    if current_user.role != "Admin":
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    project.is_deleted = True
    project.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_project",
        entity_type="project",
        entity_id=str(project_id)
    )

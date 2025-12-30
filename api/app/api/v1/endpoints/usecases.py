"""
Use Case endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.db.base import get_db
from app.models.hierarchy import Usecase, Project
from app.models.user import User
from app.schemas.hierarchy import UsecaseCreate, UsecaseUpdate, UsecaseResponse
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=List[UsecaseResponse])
async def list_usecases(
    project_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List use cases with optional filters."""
    
    from app.models.hierarchy import Program
    
    # Join through the hierarchy to apply client filtering
    query = select(Usecase).join(Project).join(Program).where(Usecase.is_deleted == False)
    
    if project_id:
        query = query.where(Usecase.project_id == project_id)
    if status:
        query = query.where(Usecase.status == status)
    if priority:
        query = query.where(Usecase.priority == priority)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.where(Program.client_id == current_user.client_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    usecases = result.scalars().all()
    
    logger.log_activity(
        action="list_usecases",
        entity_type="usecase",
        filters={
            "project_id": str(project_id) if project_id else None,
            "status": status,
            "priority": priority
        }
    )
    
    return [UsecaseResponse.from_orm(uc) for uc in usecases]


@router.get("/{usecase_id}", response_model=UsecaseResponse)
async def get_usecase(
    usecase_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific use case by ID."""
    
    from app.models.hierarchy import Program
    
    result = await db.execute(
        select(Usecase).where(
            and_(
                Usecase.id == usecase_id,
                Usecase.is_deleted == False
            )
        )
    )
    usecase = result.scalar_one_or_none()
    
    if not usecase:
        raise ResourceNotFoundException("Usecase", str(usecase_id))
    
    # Check access - traverse hierarchy to get client_id
    if current_user.role != "Admin":
        project_result = await db.execute(
            select(Project).join(Program).where(Project.id == usecase.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ResourceNotFoundException("Project", str(usecase.project_id))
        
        # Get the program to check client_id
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    logger.log_activity(
        action="view_usecase",
        entity_type="usecase",
        entity_id=str(usecase_id)
    )
    
    return UsecaseResponse.from_orm(usecase)


@router.post("/", response_model=UsecaseResponse, status_code=status.HTTP_201_CREATED)
async def create_usecase(
    usecase_data: UsecaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Project Manager", "Product Owner"]))
):
    """Create a new use case."""
    
    from app.models.hierarchy import Program
    
    # Verify project exists and get its program
    project_result = await db.execute(
        select(Project).where(Project.id == usecase_data.project_id)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project", str(usecase_data.project_id))
    
    # Check access - verify client ownership through program
    if current_user.role != "Admin":
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    usecase = Usecase(
        **usecase_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(usecase)
    await db.commit()
    await db.refresh(usecase)
    
    logger.log_activity(
        action="create_usecase",
        entity_type="usecase",
        entity_id=str(usecase.id),
        project_id=str(usecase.project_id)
    )
    
    return UsecaseResponse.from_orm(usecase)


@router.put("/{usecase_id}", response_model=UsecaseResponse)
async def update_usecase(
    usecase_id: str,
    usecase_data: UsecaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Project Manager", "Product Owner"]))
):
    """Update a use case."""
    
    from app.models.hierarchy import Program
    
    result = await db.execute(
        select(Usecase).where(
            and_(
                Usecase.id == usecase_id,
                Usecase.is_deleted == False
            )
        )
    )
    usecase = result.scalar_one_or_none()
    
    if not usecase:
        raise ResourceNotFoundException("Usecase", str(usecase_id))
    
    # Check access - traverse hierarchy
    if current_user.role != "Admin":
        project_result = await db.execute(
            select(Project).where(Project.id == usecase.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ResourceNotFoundException("Project", str(usecase.project_id))
        
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    # Update fields
    for field, value in usecase_data.dict(exclude_unset=True).items():
        setattr(usecase, field, value)
    
    usecase.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(usecase)
    
    logger.log_activity(
        action="update_usecase",
        entity_type="usecase",
        entity_id=str(usecase_id)
    )
    
    return UsecaseResponse.from_orm(usecase)


@router.delete("/{usecase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usecase(
    usecase_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Soft delete a use case."""
    
    result = await db.execute(
        select(Usecase).where(
            and_(
                Usecase.id == usecase_id,
                Usecase.is_deleted == False
            )
        )
    )
    usecase = result.scalar_one_or_none()
    
    if not usecase:
        raise ResourceNotFoundException("Usecase", str(usecase_id))
    
    # Check access
    if current_user.role != "Admin":
        project_result = await db.execute(
            select(Project).where(Project.id == usecase.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project or project.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    usecase.is_deleted = True
    usecase.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_usecase",
        entity_type="usecase",
        entity_id=str(usecase_id)
    )

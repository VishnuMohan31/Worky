"""
Program endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.db.base import get_db
from app.models.hierarchy import Program
from app.models.client import Client
from app.models.user import User
from app.schemas.hierarchy import ProgramCreate, ProgramUpdate, ProgramResponse
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=List[ProgramResponse])
async def list_programs(
    client_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List programs with optional filters."""
    
    query = select(Program).where(Program.is_deleted == False)
    
    # Apply filters
    if client_id:
        query = query.where(Program.client_id == client_id)
    if status:
        query = query.where(Program.status == status)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.where(Program.client_id == current_user.client_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    programs = result.scalars().all()
    
    return [ProgramResponse.from_orm(prog) for prog in programs]


@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(
    program_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific program by ID."""
    
    result = await db.execute(
        select(Program).where(
            and_(
                Program.id == program_id,
                Program.is_deleted == False
            )
        )
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise ResourceNotFoundException("Program", str(program_id))
    
    # Check access
    if current_user.role != "Admin" and program.client_id != current_user.client_id:
        raise AccessDeniedException()
    
    logger.log_activity(
        action="view_program",
        entity_type="program",
        entity_id=str(program_id)
    )
    
    return ProgramResponse.from_orm(program)


@router.post("/", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    program_data: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Create a new program."""
    
    # Verify client exists
    client_result = await db.execute(
        select(Client).where(Client.id == program_data.client_id)
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise ResourceNotFoundException("Client", str(program_data.client_id))
    
    # Check access
    if current_user.role != "Admin" and program_data.client_id != current_user.client_id:
        raise AccessDeniedException()
    
    program = Program(
        **program_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(program)
    await db.commit()
    await db.refresh(program)
    
    logger.log_activity(
        action="create_program",
        entity_type="program",
        entity_id=str(program.id),
        client_id=str(program.client_id)
    )
    
    return ProgramResponse.from_orm(program)


@router.put("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: str,
    program_data: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Update a program."""
    
    result = await db.execute(
        select(Program).where(
            and_(
                Program.id == program_id,
                Program.is_deleted == False
            )
        )
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise ResourceNotFoundException("Program", str(program_id))
    
    # Check access
    if current_user.role != "Admin" and program.client_id != current_user.client_id:
        raise AccessDeniedException()
    
    # Update fields
    for field, value in program_data.dict(exclude_unset=True).items():
        setattr(program, field, value)
    
    program.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(program)
    
    logger.log_activity(
        action="update_program",
        entity_type="program",
        entity_id=str(program_id)
    )
    
    return ProgramResponse.from_orm(program)


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Soft delete a program."""
    
    result = await db.execute(
        select(Program).where(
            and_(
                Program.id == program_id,
                Program.is_deleted == False
            )
        )
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise ResourceNotFoundException("Program", str(program_id))
    
    # Check access
    if current_user.role != "Admin" and program.client_id != current_user.client_id:
        raise AccessDeniedException()
    
    program.is_deleted = True
    program.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_program",
        entity_type="program",
        entity_id=str(program_id)
    )

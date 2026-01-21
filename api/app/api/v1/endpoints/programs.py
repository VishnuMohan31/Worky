"""
Program endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import date

from app.db.base import get_db
from app.models.hierarchy import Program
from app.models.client import Client
from app.models.user import User
from app.schemas.hierarchy import ProgramCreate, ProgramUpdate, ProgramResponse, parse_ddmmyyyy_date, format_date_to_ddmmyyyy
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


def convert_dates_for_db(data_dict: dict) -> dict:
    """Convert DD/MM/YYYY dates to date objects for database storage"""
    converted = data_dict.copy()
    
    for field in ['start_date', 'end_date']:
        if field in converted and converted[field]:
            try:
                converted[field] = parse_ddmmyyyy_date(converted[field])
            except ValueError:
                # If parsing fails, leave as is (will be caught by validation)
                pass
    
    return converted


def convert_dates_for_response(program) -> dict:
    """Convert date objects to DD/MM/YYYY format for response"""
    program_dict = ProgramResponse.from_orm(program).dict()
    
    # Convert dates to DD/MM/YYYY format
    if program_dict.get('start_date'):
        program_dict['start_date'] = format_date_to_ddmmyyyy(program.start_date)
    if program_dict.get('end_date'):
        program_dict['end_date'] = format_date_to_ddmmyyyy(program.end_date)
    
    return program_dict


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
    
    # Convert dates to DD/MM/YYYY format for response
    response_list = []
    for prog in programs:
        prog_dict = convert_dates_for_response(prog)
        response_list.append(ProgramResponse(**prog_dict))
    
    return response_list


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
    
    # Convert dates to DD/MM/YYYY format for response
    prog_dict = convert_dates_for_response(program)
    return ProgramResponse(**prog_dict)


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
    
    # Convert DD/MM/YYYY dates to date objects for database
    program_dict = convert_dates_for_db(program_data.dict())
    
    program = Program(
        **program_dict,
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
    
    # Convert dates back to DD/MM/YYYY format for response
    prog_dict = convert_dates_for_response(program)
    return ProgramResponse(**prog_dict)


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
    
    # Convert DD/MM/YYYY dates to date objects for database
    update_data = convert_dates_for_db(program_data.dict(exclude_unset=True))
    
    # Get current dates if not being updated (for validation)
    start_date = update_data.get('start_date', program.start_date)
    end_date = update_data.get('end_date', program.end_date)
    
    # Validate date range if both dates exist
    if start_date and end_date and end_date < start_date:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )
    
    # Update fields
    for field, value in update_data.items():
        setattr(program, field, value)
    
    program.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(program)
    
    logger.log_activity(
        action="update_program",
        entity_type="program",
        entity_id=str(program_id)
    )
    
    # Convert dates back to DD/MM/YYYY format for response
    prog_dict = convert_dates_for_response(program)
    return ProgramResponse(**prog_dict)


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

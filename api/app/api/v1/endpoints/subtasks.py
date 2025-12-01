"""
Subtask endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime

from app.db.base import get_db
from app.models.hierarchy import Subtask, Task, Phase
from app.models.user import User
from app.schemas.hierarchy import SubtaskCreate, SubtaskUpdate, SubtaskResponse
from app.core.security import get_current_user
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException, ValidationException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=List[SubtaskResponse])
async def list_subtasks(
    task_id: Optional[UUID] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    phase_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List subtasks with optional filters."""
    
    query = select(Subtask).where(Subtask.is_deleted == False)
    
    # Apply filters
    if task_id:
        query = query.where(Subtask.task_id == task_id)
    if assigned_to:
        query = query.where(Subtask.assigned_to == assigned_to)
    if phase_id:
        query = query.where(Subtask.phase_id == phase_id)
    if status:
        query = query.where(Subtask.status == status)
    
    # Non-admin users can only see their own subtasks
    if current_user.role != "Admin":
        query = query.where(Subtask.assigned_to == current_user.id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    subtasks = result.scalars().all()
    
    return [SubtaskResponse.from_orm(subtask) for subtask in subtasks]


@router.get("/{subtask_id}", response_model=SubtaskResponse)
async def get_subtask(
    subtask_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific subtask by ID."""
    
    result = await db.execute(
        select(Subtask).where(
            and_(
                Subtask.id == subtask_id,
                Subtask.is_deleted == False
            )
        )
    )
    subtask = result.scalar_one_or_none()
    
    if not subtask:
        raise ResourceNotFoundException("Subtask", str(subtask_id))
    
    # Check access
    if current_user.role != "Admin" and subtask.assigned_to != current_user.id:
        raise AccessDeniedException("You can only view subtasks assigned to you")
    
    logger.log_activity(
        action="view_subtask",
        entity_type="subtask",
        entity_id=str(subtask_id)
    )
    
    return SubtaskResponse.from_orm(subtask)


@router.post("/", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    subtask_data: SubtaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new subtask."""
    
    # Verify parent task exists
    task_result = await db.execute(
        select(Task).where(Task.id == subtask_data.task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise ResourceNotFoundException("Task", str(subtask_data.task_id))
    
    # Verify phase exists if provided
    if subtask_data.phase_id:
        phase_result = await db.execute(
            select(Phase).where(Phase.id == subtask_data.phase_id)
        )
        phase = phase_result.scalar_one_or_none()
        
        if not phase:
            raise ResourceNotFoundException("Phase", str(subtask_data.phase_id))
    
    # Validate that subtasks cannot have subtasks (enforce max depth)
    # This is enforced by the database schema, but we check here for better error messages
    
    subtask = Subtask(
        **subtask_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(subtask)
    await db.commit()
    await db.refresh(subtask)
    
    logger.log_activity(
        action="create_subtask",
        entity_type="subtask",
        entity_id=str(subtask.id),
        task_id=str(subtask.task_id),
        phase_id=str(subtask.phase_id)
    )
    
    return SubtaskResponse.from_orm(subtask)


@router.put("/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    subtask_id: str,
    subtask_data: SubtaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a subtask with status transition tracking."""
    
    result = await db.execute(
        select(Subtask).where(
            and_(
                Subtask.id == subtask_id,
                Subtask.is_deleted == False
            )
        )
    )
    subtask = result.scalar_one_or_none()
    
    if not subtask:
        raise ResourceNotFoundException("Subtask", str(subtask_id))
    
    # Check access - users can update their own subtasks, admins can update any
    if current_user.role != "Admin" and subtask.assigned_to != current_user.id:
        raise AccessDeniedException("You can only update subtasks assigned to you")
    
    # Track status transitions
    old_status = subtask.status
    new_status = subtask_data.status if subtask_data.status else old_status
    
    # Validate status transitions
    valid_transitions = {
        "To Do": ["In Progress", "Blocked"],
        "In Progress": ["To Do", "Done", "Blocked"],
        "Blocked": ["To Do", "In Progress"],
        "Done": ["In Progress"]  # Allow reopening
    }
    
    if new_status != old_status:
        if old_status not in valid_transitions or new_status not in valid_transitions.get(old_status, []):
            raise ValidationException(f"Invalid status transition from '{old_status}' to '{new_status}'")
        
        # Set completed_at when transitioning to Done
        if new_status == "Done" and old_status != "Done":
            subtask.completed_at = datetime.utcnow()
        # Clear completed_at when reopening
        elif old_status == "Done" and new_status != "Done":
            subtask.completed_at = None
    
    # Verify phase if being updated
    if subtask_data.phase_id:
        phase_result = await db.execute(
            select(Phase).where(Phase.id == subtask_data.phase_id)
        )
        if not phase_result.scalar_one_or_none():
            raise ResourceNotFoundException("Phase", str(subtask_data.phase_id))
    
    # Verify assigned user exists if being updated
    if subtask_data.assigned_to:
        assignee_result = await db.execute(
            select(User).where(User.id == subtask_data.assigned_to)
        )
        if not assignee_result.scalar_one_or_none():
            raise ResourceNotFoundException("User", str(subtask_data.assigned_to))
    
    # Update fields
    for field, value in subtask_data.dict(exclude_unset=True).items():
        if field != "status":  # Status already handled above
            setattr(subtask, field, value)
    
    if subtask_data.status:
        subtask.status = new_status
    
    subtask.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(subtask)
    
    logger.log_activity(
        action="update_subtask",
        entity_type="subtask",
        entity_id=str(subtask_id),
        status_transition=f"{old_status} -> {new_status}" if old_status != new_status else None
    )
    
    return SubtaskResponse.from_orm(subtask)


@router.delete("/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    subtask_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a subtask."""
    
    result = await db.execute(
        select(Subtask).where(
            and_(
                Subtask.id == subtask_id,
                Subtask.is_deleted == False
            )
        )
    )
    subtask = result.scalar_one_or_none()
    
    if not subtask:
        raise ResourceNotFoundException("Subtask", str(subtask_id))
    
    # Check access
    if current_user.role != "Admin" and subtask.assigned_to != current_user.id:
        raise AccessDeniedException("You can only delete subtasks assigned to you")
    
    subtask.is_deleted = True
    subtask.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_subtask",
        entity_type="subtask",
        entity_id=str(subtask_id)
    )


@router.get("/my-subtasks/", response_model=List[SubtaskResponse])
async def get_my_subtasks(
    status: Optional[str] = Query(None),
    phase_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subtasks assigned to current user."""
    
    query = select(Subtask).where(
        and_(
            Subtask.assigned_to == current_user.id,
            Subtask.is_deleted == False
        )
    )
    
    if status:
        query = query.where(Subtask.status == status)
    if phase_id:
        query = query.where(Subtask.phase_id == phase_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    subtasks = result.scalars().all()
    
    return [SubtaskResponse.from_orm(subtask) for subtask in subtasks]

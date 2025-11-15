"""
Phase management endpoints for the Worky API.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from uuid import UUID

from app.db.base import get_db
from app.models.hierarchy import Phase, Task, Subtask
from app.models.user import User
from app.schemas.hierarchy import PhaseCreate, PhaseUpdate, PhaseResponse
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, ValidationException, ConflictException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=List[PhaseResponse])
async def list_phases(
    include_inactive: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all phases."""
    
    query = select(Phase).where(Phase.is_deleted == False)
    
    if not include_inactive:
        query = query.where(Phase.is_active == True)
    
    query = query.order_by(Phase.display_order, Phase.name)
    result = await db.execute(query)
    phases = result.scalars().all()
    
    return [PhaseResponse.from_orm(phase) for phase in phases]


@router.get("/{phase_id}", response_model=PhaseResponse)
async def get_phase(
    phase_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific phase by ID."""
    
    result = await db.execute(
        select(Phase).where(
            and_(
                Phase.id == phase_id,
                Phase.is_deleted == False
            )
        )
    )
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise ResourceNotFoundException("Phase", str(phase_id))
    
    return PhaseResponse.from_orm(phase)


@router.post("/", response_model=PhaseResponse, status_code=status.HTTP_201_CREATED)
async def create_phase(
    phase_data: PhaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Create a new phase (Admin only)."""
    
    # Check if phase name already exists
    existing_result = await db.execute(
        select(Phase).where(
            and_(
                Phase.name == phase_data.name,
                Phase.is_deleted == False
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise ConflictException(
            f"Phase with name '{phase_data.name}' already exists"
        )
    
    phase = Phase(
        **phase_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(phase)
    await db.commit()
    await db.refresh(phase)
    
    logger.log_activity(
        action="create_phase",
        entity_type="phase",
        entity_id=str(phase.id),
        phase_name=phase.name
    )
    
    return PhaseResponse.from_orm(phase)


@router.put("/{phase_id}", response_model=PhaseResponse)
async def update_phase(
    phase_id: str,
    phase_data: PhaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Update a phase (Admin only)."""
    
    result = await db.execute(
        select(Phase).where(
            and_(
                Phase.id == phase_id,
                Phase.is_deleted == False
            )
        )
    )
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise ResourceNotFoundException("Phase", str(phase_id))
    
    # Check if new name conflicts with existing phase
    if phase_data.name and phase_data.name != phase.name:
        existing_result = await db.execute(
            select(Phase).where(
                and_(
                    Phase.name == phase_data.name,
                    Phase.id != phase_id,
                    Phase.is_deleted == False
                )
            )
        )
        if existing_result.scalar_one_or_none():
            raise ConflictException(
                f"Phase with name '{phase_data.name}' already exists"
            )
    
    # Update fields
    for field, value in phase_data.dict(exclude_unset=True).items():
        setattr(phase, field, value)
    
    phase.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(phase)
    
    logger.log_activity(
        action="update_phase",
        entity_type="phase",
        entity_id=str(phase_id),
        changes=phase_data.dict(exclude_unset=True)
    )
    
    return PhaseResponse.from_orm(phase)


@router.post("/{phase_id}/deactivate")
async def deactivate_phase(
    phase_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Deactivate a phase (Admin only). Cannot deactivate if in use."""
    
    result = await db.execute(
        select(Phase).where(
            and_(
                Phase.id == phase_id,
                Phase.is_deleted == False
            )
        )
    )
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise ResourceNotFoundException("Phase", str(phase_id))
    
    # Check if phase is in use
    task_count_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.phase_id == phase_id,
                Task.is_deleted == False
            )
        )
    )
    task_count = task_count_result.scalar()
    
    subtask_count_result = await db.execute(
        select(func.count(Subtask.id)).where(
            and_(
                Subtask.phase_id == phase_id,
                Subtask.is_deleted == False
            )
        )
    )
    subtask_count = subtask_count_result.scalar()
    
    total_usage = task_count + subtask_count
    
    if total_usage > 0:
        raise ValidationException(
            f"Cannot deactivate phase: {total_usage} tasks/subtasks are using it",
            details={
                "task_count": task_count,
                "subtask_count": subtask_count,
                "total_usage": total_usage
            }
        )
    
    phase.is_active = False
    phase.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(phase)
    
    logger.log_activity(
        action="deactivate_phase",
        entity_type="phase",
        entity_id=str(phase_id)
    )
    
    return {"message": "Phase deactivated successfully", "phase": PhaseResponse.from_orm(phase)}


@router.get("/{phase_id}/usage")
async def get_phase_usage(
    phase_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get usage statistics for a phase."""
    
    result = await db.execute(
        select(Phase).where(
            and_(
                Phase.id == phase_id,
                Phase.is_deleted == False
            )
        )
    )
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise ResourceNotFoundException("Phase", str(phase_id))
    
    # Count tasks using this phase
    task_count_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.phase_id == phase_id,
                Task.is_deleted == False
            )
        )
    )
    task_count = task_count_result.scalar()
    
    # Count subtasks using this phase
    subtask_count_result = await db.execute(
        select(func.count(Subtask.id)).where(
            and_(
                Subtask.phase_id == phase_id,
                Subtask.is_deleted == False
            )
        )
    )
    subtask_count = subtask_count_result.scalar()
    
    # Get task status breakdown
    task_status_result = await db.execute(
        select(Task.status, func.count(Task.id)).where(
            and_(
                Task.phase_id == phase_id,
                Task.is_deleted == False
            )
        ).group_by(Task.status)
    )
    task_status_breakdown = {status: count for status, count in task_status_result.all()}
    
    # Get subtask status breakdown
    subtask_status_result = await db.execute(
        select(Subtask.status, func.count(Subtask.id)).where(
            and_(
                Subtask.phase_id == phase_id,
                Subtask.is_deleted == False
            )
        ).group_by(Subtask.status)
    )
    subtask_status_breakdown = {status: count for status, count in subtask_status_result.all()}
    
    return {
        "phase": PhaseResponse.from_orm(phase),
        "usage": {
            "total_count": task_count + subtask_count,
            "task_count": task_count,
            "subtask_count": subtask_count,
            "task_status_breakdown": task_status_breakdown,
            "subtask_status_breakdown": subtask_status_breakdown
        }
    }


@router.delete("/{phase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phase(
    phase_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Soft delete a phase (Admin only). Cannot delete if in use."""
    
    result = await db.execute(
        select(Phase).where(
            and_(
                Phase.id == phase_id,
                Phase.is_deleted == False
            )
        )
    )
    phase = result.scalar_one_or_none()
    
    if not phase:
        raise ResourceNotFoundException("Phase", str(phase_id))
    
    # Check if phase is in use
    task_count_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.phase_id == phase_id,
                Task.is_deleted == False
            )
        )
    )
    task_count = task_count_result.scalar()
    
    subtask_count_result = await db.execute(
        select(func.count(Subtask.id)).where(
            and_(
                Subtask.phase_id == phase_id,
                Subtask.is_deleted == False
            )
        )
    )
    subtask_count = subtask_count_result.scalar()
    
    total_usage = task_count + subtask_count
    
    if total_usage > 0:
        raise ValidationException(
            f"Cannot delete phase: {total_usage} tasks/subtasks are using it",
            details={
                "task_count": task_count,
                "subtask_count": subtask_count,
                "total_usage": total_usage
            }
        )
    
    phase.is_deleted = True
    phase.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_phase",
        entity_type="phase",
        entity_id=str(phase_id)
    )

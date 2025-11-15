"""
Bug tracking endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from uuid import UUID
from datetime import datetime

from app.db.base import get_db
from app.models.bug import Bug
from app.models.user import User
from app.schemas.bug import BugCreate, BugUpdate, BugResponse, BugList
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException, ValidationException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=BugList)
async def list_bugs(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[UUID] = Query(None),
    severity: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    reported_by: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List bugs with optional filters."""
    
    query = select(Bug).where(Bug.is_deleted == False)
    
    # Apply filters
    if entity_type:
        query = query.where(Bug.entity_type == entity_type)
    if entity_id:
        query = query.where(Bug.entity_id == entity_id)
    if severity:
        query = query.where(Bug.severity == severity)
    if priority:
        query = query.where(Bug.priority == priority)
    if status:
        query = query.where(Bug.status == status)
    if assigned_to:
        query = query.where(Bug.assigned_to == assigned_to)
    if reported_by:
        query = query.where(Bug.reported_by == reported_by)
    
    # Count total
    count_query = select(Bug).where(Bug.is_deleted == False)
    if entity_type:
        count_query = count_query.where(Bug.entity_type == entity_type)
    if entity_id:
        count_query = count_query.where(Bug.entity_id == entity_id)
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.order_by(Bug.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    bugs = result.scalars().all()
    
    return BugList(
        bugs=[BugResponse.from_orm(bug) for bug in bugs],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        has_more=(skip + limit) < total
    )


@router.get("/{bug_id}", response_model=BugResponse)
async def get_bug(
    bug_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific bug by ID."""
    
    result = await db.execute(
        select(Bug).where(
            and_(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
    )
    bug = result.scalar_one_or_none()
    
    if not bug:
        raise ResourceNotFoundException("Bug", str(bug_id))
    
    logger.log_activity(
        action="view_bug",
        entity_type="bug",
        entity_id=str(bug_id)
    )
    
    return BugResponse.from_orm(bug)


@router.post("/", response_model=BugResponse, status_code=status.HTTP_201_CREATED)
async def create_bug(
    bug_data: BugCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bug."""
    
    # Validate entity type
    valid_entity_types = ["Program", "Project", "UseCase", "UserStory", "Task", "Subtask"]
    if bug_data.entity_type not in valid_entity_types:
        raise ValidationException(
            f"Invalid entity_type. Must be one of: {', '.join(valid_entity_types)}"
        )
    
    # Validate severity
    valid_severities = ["Critical", "High", "Medium", "Low"]
    if bug_data.severity not in valid_severities:
        raise ValidationException(
            f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
        )
    
    # Validate priority
    valid_priorities = ["P0", "P1", "P2", "P3"]
    if bug_data.priority not in valid_priorities:
        raise ValidationException(
            f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        )
    
    bug = Bug(
        **bug_data.dict(),
        reported_by=str(current_user.id),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(bug)
    await db.commit()
    await db.refresh(bug)
    
    logger.log_activity(
        action="create_bug",
        entity_type="bug",
        entity_id=str(bug.id),
        severity=bug.severity,
        priority=bug.priority,
        associated_entity_type=bug.entity_type,
        associated_entity_id=str(bug.entity_id)
    )
    
    return BugResponse.from_orm(bug)


@router.put("/{bug_id}", response_model=BugResponse)
async def update_bug(
    bug_id: str,
    bug_data: BugUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a bug."""
    
    result = await db.execute(
        select(Bug).where(
            and_(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
    )
    bug = result.scalar_one_or_none()
    
    if not bug:
        raise ResourceNotFoundException("Bug", str(bug_id))
    
    # Check if user can update (reporter, assignee, or admin)
    if current_user.role not in ["Admin", "Tester"]:
        if str(bug.reported_by) != str(current_user.id) and str(bug.assigned_to) != str(current_user.id):
            raise AccessDeniedException("You can only update bugs you reported or are assigned to")
    
    # Update fields
    for field, value in bug_data.dict(exclude_unset=True).items():
        setattr(bug, field, value)
    
    bug.updated_by = str(current_user.id)
    
    # If status changed to closed, set closed_at
    if bug_data.status and bug_data.status.lower() in ["closed", "resolved"]:
        bug.closed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(bug)
    
    logger.log_activity(
        action="update_bug",
        entity_type="bug",
        entity_id=str(bug_id),
        changes=bug_data.dict(exclude_unset=True)
    )
    
    return BugResponse.from_orm(bug)


@router.post("/{bug_id}/assign")
async def assign_bug(
    bug_id: str,
    assignee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Tester", "Project Manager"]))
):
    """Assign a bug to a user."""
    
    result = await db.execute(
        select(Bug).where(
            and_(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
    )
    bug = result.scalar_one_or_none()
    
    if not bug:
        raise ResourceNotFoundException("Bug", str(bug_id))
    
    # Verify assignee exists
    assignee_result = await db.execute(
        select(User).where(User.id == assignee_id)
    )
    assignee = assignee_result.scalar_one_or_none()
    
    if not assignee:
        raise ResourceNotFoundException("User", str(assignee_id))
    
    bug.assigned_to = str(assignee_id)
    bug.status = "Assigned"
    bug.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(bug)
    
    logger.log_activity(
        action="assign_bug",
        entity_type="bug",
        entity_id=str(bug_id),
        assignee_id=str(assignee_id)
    )
    
    return {"message": "Bug assigned successfully", "bug": BugResponse.from_orm(bug)}


@router.post("/{bug_id}/resolve")
async def resolve_bug(
    bug_id: str,
    resolution_notes: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a bug as resolved."""
    
    result = await db.execute(
        select(Bug).where(
            and_(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
    )
    bug = result.scalar_one_or_none()
    
    if not bug:
        raise ResourceNotFoundException("Bug", str(bug_id))
    
    # Check if user can resolve (assignee, tester, or admin)
    if current_user.role not in ["Admin", "Tester"]:
        if str(bug.assigned_to) != str(current_user.id):
            raise AccessDeniedException("You can only resolve bugs assigned to you")
    
    bug.status = "Resolved"
    bug.resolution_notes = resolution_notes
    bug.closed_at = datetime.utcnow()
    bug.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(bug)
    
    logger.log_activity(
        action="resolve_bug",
        entity_type="bug",
        entity_id=str(bug_id)
    )
    
    return {"message": "Bug resolved successfully", "bug": BugResponse.from_orm(bug)}


@router.delete("/{bug_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bug(
    bug_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Tester"]))
):
    """Soft delete a bug."""
    
    result = await db.execute(
        select(Bug).where(
            and_(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
    )
    bug = result.scalar_one_or_none()
    
    if not bug:
        raise ResourceNotFoundException("Bug", str(bug_id))
    
    bug.is_deleted = True
    bug.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_bug",
        entity_type="bug",
        entity_id=str(bug_id)
    )

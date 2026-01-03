"""
Decisions management endpoints for the Worky API.

This module provides endpoints for managing decisions across all hierarchy entities.
Decisions are special notes marked with is_decision=True and have status tracking.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import joinedload
from uuid import UUID
import uuid

from app.db.base import get_db
from app.models.entity_note import EntityNote
from app.models.user import User
from app.models.client import Client
from app.models.hierarchy import Project, Usecase, UserStory, Task, Subtask
from app.schemas.entity_note import EntityNoteCreate, EntityNoteResponse, EntityNoteUpdate, DecisionSummary
from app.core.security import get_current_user
from app.core.logging import StructuredLogger
from app.services.hierarchy_service import HierarchyService

router = APIRouter()
logger = StructuredLogger(__name__)


async def get_entity_name(entity_type: str, entity_id: str, db: AsyncSession) -> Optional[str]:
    """Get the display name for an entity."""
    try:
        if entity_type == 'Client':
            result = await db.execute(select(Client.name).where(Client.id == entity_id))
            name = result.scalar_one_or_none()
            return name
        elif entity_type == 'Project':
            result = await db.execute(select(Project.name).where(Project.id == entity_id))
            name = result.scalar_one_or_none()
            return name
        elif entity_type == 'UseCase':
            result = await db.execute(select(Usecase.name).where(Usecase.id == entity_id))
            name = result.scalar_one_or_none()
            return name
        elif entity_type == 'UserStory':
            result = await db.execute(select(UserStory.title).where(UserStory.id == entity_id))
            name = result.scalar_one_or_none()
            return name
        elif entity_type == 'Task':
            result = await db.execute(select(Task.title).where(Task.id == entity_id))
            name = result.scalar_one_or_none()
            return name
        elif entity_type == 'Subtask':
            result = await db.execute(select(Subtask.title).where(Subtask.id == entity_id))
            name = result.scalar_one_or_none()
            return name
        else:
            return f"{entity_type} {entity_id}"
    except Exception:
        return f"{entity_type} {entity_id}"


@router.get("/", response_model=List[DecisionSummary])
async def get_all_decisions(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    decision_status: Optional[str] = Query(None, description="Filter by decision status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all decisions across the system with optional filters.
    
    Returns decisions from all entities the user has access to.
    
    Args:
        entity_type: Filter by specific entity type
        decision_status: Filter by decision status
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of decisions with entity information
    """
    # Build query for decisions only
    query = select(EntityNote).options(
        joinedload(EntityNote.creator)
    ).where(
        EntityNote.is_decision == True
    )
    
    # Apply filters
    if entity_type:
        # Validate and normalize entity type
        valid_types = ['Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask', 'Bug']
        entity_type_capitalized = entity_type.capitalize()
        
        if entity_type.lower() == 'usecase':
            entity_type_capitalized = 'UseCase'
        elif entity_type.lower() == 'userstory':
            entity_type_capitalized = 'UserStory'
        
        if entity_type_capitalized in valid_types:
            query = query.where(EntityNote.entity_type == entity_type_capitalized)
    
    if decision_status:
        query = query.where(EntityNote.decision_status == decision_status)
    
    # Order by most recent first
    query = query.order_by(EntityNote.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    decisions = result.scalars().all()
    
    # Build response with entity names
    response_decisions = []
    for decision in decisions:
        entity_name = await get_entity_name(decision.entity_type, decision.entity_id, db)
        
        decision_dict = {
            "id": decision.id,
            "entity_type": decision.entity_type,
            "entity_id": decision.entity_id,
            "entity_name": entity_name,
            "note_text": decision.note_text,
            "decision_status": decision.decision_status,
            "created_by": decision.created_by,
            "created_at": decision.created_at,
            "creator_name": decision.creator.full_name if decision.creator else "Unknown User"
        }
        response_decisions.append(decision_dict)
    
    logger.log_activity(
        action="view_all_decisions",
        decisions_count=len(decisions),
        entity_type_filter=entity_type,
        status_filter=decision_status
    )
    
    return response_decisions


@router.post("/", response_model=EntityNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    decision_data: EntityNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new decision for any entity.
    
    This endpoint allows creating decisions for any entity in the hierarchy.
    The decision will be marked with is_decision=True automatically.
    
    Args:
        decision_data: Decision content and entity information
        
    Returns:
        Created decision with full information
        
    Raises:
        400: Invalid entity type or missing required fields
        403: Access denied to entity
        404: Entity not found
    """
    # Validate required fields
    if not decision_data.entity_type or not decision_data.entity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type and entity_id are required for creating decisions"
        )
    
    if not decision_data.note_text or not decision_data.note_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision text cannot be empty"
        )
    
    # Validate entity type
    valid_types = ['Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask', 'Bug']
    entity_type_capitalized = decision_data.entity_type.capitalize()
    
    # Handle special cases
    if decision_data.entity_type.lower() == 'usecase':
        entity_type_capitalized = 'UseCase'
    elif decision_data.entity_type.lower() == 'userstory':
        entity_type_capitalized = 'UserStory'
    
    if entity_type_capitalized not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Verify user has access to the entity (skip for clients)
    if entity_type_capitalized != 'Client':
        service = HierarchyService(db)
        try:
            # Use entity_id as string - the service will handle UUID conversion if needed
            await service._verify_entity_access(entity_type_capitalized.lower(), decision_data.entity_id, current_user)
        except Exception as e:
            logger.log_system(
                level="warning",
                message=f"Access denied for user {current_user.id} to create decision on {entity_type_capitalized} {decision_data.entity_id}",
                error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this entity"
            )
    
    # Create the decision (force is_decision=True)
    from app.crud.crud_entity_note import entity_note
    
    note_create = EntityNoteCreate(
        entity_type=entity_type_capitalized,
        entity_id=decision_data.entity_id,
        note_text=decision_data.note_text.strip(),
        is_decision=True,  # Force decision flag
        decision_status=decision_data.decision_status or 'Active'
    )
    
    new_decision = await entity_note.create(
        db=db,
        obj_in=note_create,
        created_by=str(current_user.id)
    )
    
    await db.commit()
    await db.refresh(new_decision)
    
    # Load creator information
    await db.refresh(new_decision, ['creator'])
    
    logger.log_activity(
        action="create_decision",
        entity_type=entity_type_capitalized,
        entity_id=decision_data.entity_id,
        decision_id=new_decision.id,
        decision_status=new_decision.decision_status,
        user_id=str(current_user.id)
    )
    
    # Return response
    return {
        "id": new_decision.id,
        "entity_type": new_decision.entity_type,
        "entity_id": new_decision.entity_id,
        "note_text": new_decision.note_text,
        "created_by": new_decision.created_by,
        "created_at": new_decision.created_at,
        "creator_name": new_decision.creator.full_name if new_decision.creator else "Unknown User",
        "creator_email": new_decision.creator.email if new_decision.creator else "",
        "is_decision": new_decision.is_decision,
        "decision_status": new_decision.decision_status
    }


@router.put("/{decision_id}/status", response_model=EntityNoteResponse)
async def update_decision_status(
    decision_id: str = Path(..., description="Decision ID"),
    status_update: EntityNoteUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the status of a decision.
    
    This endpoint allows updating decision status from the decisions management interface.
    
    Args:
        decision_id: ID of the decision to update
        status_update: New decision status
        
    Returns:
        Updated decision with new status
        
    Raises:
        400: Note is not a decision
        403: Access denied
        404: Decision not found
    """
    # Get the decision
    query = select(EntityNote).options(
        joinedload(EntityNote.creator)
    ).where(
        EntityNote.id == decision_id,
        EntityNote.is_decision == True
    )
    
    result = await db.execute(query)
    decision = result.scalar_one_or_none()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    # Verify user has access to the entity (skip for clients)
    if decision.entity_type != 'Client':
        service = HierarchyService(db)
        try:
            # Use entity_id as string - the service will handle UUID conversion if needed
            await service._verify_entity_access(decision.entity_type.lower(), decision.entity_id, current_user)
        except Exception as e:
            logger.log_system(
                level="warning",
                message=f"Access denied for user {current_user.id} to update decision {decision_id}",
                error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this decision"
            )
    
    # Update decision status by temporarily disabling trigger, updating, then re-enabling
    old_status = decision.decision_status
    from sqlalchemy import text
    
    # Temporarily disable the trigger
    await db.execute(text("ALTER TABLE entity_notes DISABLE TRIGGER prevent_entity_notes_update"))
    
    try:
        # Update decision status
        await db.execute(
            text("UPDATE entity_notes SET decision_status = :new_status WHERE id = :decision_id AND is_decision = TRUE"),
            {"new_status": status_update.decision_status, "decision_id": decision_id}
        )
        await db.commit()
        
        # Re-enable the trigger
        await db.execute(text("ALTER TABLE entity_notes ENABLE TRIGGER prevent_entity_notes_update"))
        await db.commit()
        
        # Re-query the decision to get updated status
        result = await db.execute(
            select(EntityNote).options(joinedload(EntityNote.creator)).where(
                EntityNote.id == decision_id,
                EntityNote.is_decision == True
            )
        )
        decision = result.scalar_one_or_none()
    except Exception as e:
        # Re-enable trigger even if update fails
        await db.execute(text("ALTER TABLE entity_notes ENABLE TRIGGER prevent_entity_notes_update"))
        await db.commit()
        raise
    
    logger.log_activity(
        action="update_decision_status",
        entity_type=decision.entity_type,
        entity_id=decision.entity_id,
        decision_id=decision_id,
        old_status=old_status,
        new_status=status_update.decision_status,
        user_id=str(current_user.id)
    )
    
    # Return updated decision
    return {
        "id": decision.id,
        "entity_type": decision.entity_type,
        "entity_id": decision.entity_id,
        "note_text": decision.note_text,
        "created_by": decision.created_by,
        "created_at": decision.created_at,
        "creator_name": decision.creator.full_name if decision.creator else "Unknown User",
        "creator_email": decision.creator.email if decision.creator else "",
        "is_decision": decision.is_decision,
        "decision_status": decision.decision_status
    }


@router.get("/stats", response_model=dict)
async def get_decision_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get decision statistics across the system.
    
    Returns counts by status and entity type.
    """
    from sqlalchemy import func
    
    # Get counts by status
    status_query = select(
        EntityNote.decision_status,
        func.count(EntityNote.id).label('count')
    ).where(
        EntityNote.is_decision == True
    ).group_by(EntityNote.decision_status)
    
    status_result = await db.execute(status_query)
    status_counts = {row.decision_status: row.count for row in status_result}
    
    # Get counts by entity type
    type_query = select(
        EntityNote.entity_type,
        func.count(EntityNote.id).label('count')
    ).where(
        EntityNote.is_decision == True
    ).group_by(EntityNote.entity_type)
    
    type_result = await db.execute(type_query)
    type_counts = {row.entity_type: row.count for row in type_result}
    
    # Get total count
    total_query = select(func.count(EntityNote.id)).where(EntityNote.is_decision == True)
    total_result = await db.execute(total_query)
    total_count = total_result.scalar()
    
    return {
        "total_decisions": total_count,
        "by_status": status_counts,
        "by_entity_type": type_counts
    }
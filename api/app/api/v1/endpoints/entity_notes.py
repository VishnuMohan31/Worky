"""
Entity Notes endpoints for the Worky API.

This module provides endpoints for managing notes/comments on any entity in the hierarchy.
Notes are immutable once created and displayed in reverse chronological order.

Requirements: Comments on any hierarchy element with user names in time series
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.db.base import get_db
from app.models.entity_note import EntityNote
from app.models.user import User
from app.schemas.entity_note import EntityNoteCreate, EntityNoteResponse, EntityNoteUpdate
from app.core.security import get_current_user
from app.core.logging import StructuredLogger
from app.services.hierarchy_service import HierarchyService

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/{entity_type}/{entity_id}/notes", response_model=List[EntityNoteResponse])
async def get_entity_notes(
    entity_type: str = Path(..., description="Entity type (Client, Program, Project, UseCase, UserStory, Task, Subtask, Bug)"),
    entity_id: str = Path(..., description="Entity ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    decisions_only: bool = Query(False, description="Filter to show only decisions"),
    notes_only: bool = Query(False, description="Filter to show only regular notes (not decisions)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notes for a specific entity in reverse chronological order.
    
    Only users assigned to the project or entity can view notes.
    
    Args:
        entity_type: Type of entity (Client, Program, Project, UseCase, UserStory, Task, Subtask, Bug)
        entity_id: ID of the entity
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of notes with creator information, ordered by most recent first
        
    Raises:
        400: Invalid entity type
        403: Access denied
        404: Entity not found
    """
    # Validate entity type
    valid_types = ['Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask', 'Bug']
    entity_type_capitalized = entity_type.capitalize()
    
    # Handle special cases
    if entity_type.lower() == 'usecase':
        entity_type_capitalized = 'UseCase'
    elif entity_type.lower() == 'userstory':
        entity_type_capitalized = 'UserStory'
    
    if entity_type_capitalized not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Verify user has access to the entity
    # For clients, skip access verification as all authenticated users can access
    if entity_type_capitalized != 'Client':
        service = HierarchyService(db)
        try:
            # Convert entity_id to UUID if needed
            entity_uuid = UUID(entity_id) if len(entity_id) > 20 else entity_id
            await service._verify_entity_access(entity_type.lower(), entity_uuid, current_user)
        except Exception as e:
            logger.log_system(
                level="warning",
                message=f"Access denied for user {current_user.id} to {entity_type} {entity_id}",
                error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this entity"
            )
    
    # Build query with filters
    query = select(EntityNote).options(
        joinedload(EntityNote.creator)
    ).where(
        EntityNote.entity_type == entity_type_capitalized,
        EntityNote.entity_id == entity_id
    )
    
    # Apply decision filters
    if decisions_only:
        query = query.where(EntityNote.is_decision == True)
    elif notes_only:
        query = query.where(EntityNote.is_decision == False)
    
    query = query.order_by(
        EntityNote.created_at.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    notes = result.scalars().all()
    
    logger.log_activity(
        action="view_entity_notes",
        entity_type=entity_type_capitalized,
        entity_id=entity_id,
        notes_count=len(notes)
    )
    
    # Convert to response with creator name and decision info
    response_notes = []
    for note in notes:
        note_dict = {
            "id": note.id,
            "entity_type": note.entity_type,
            "entity_id": note.entity_id,
            "note_text": note.note_text,
            "created_by": note.created_by,
            "created_at": note.created_at,
            "creator_name": note.creator.full_name if note.creator else "Unknown User",
            "creator_email": note.creator.email if note.creator else "",
            "is_decision": note.is_decision,
            "decision_status": note.decision_status if note.is_decision else None
        }
        response_notes.append(note_dict)
    
    return response_notes


@router.post("/{entity_type}/{entity_id}/notes", response_model=EntityNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_entity_note(
    entity_type: str = Path(..., description="Entity type (Client, Program, Project, UseCase, UserStory, Task, Subtask, Bug)"),
    entity_id: str = Path(..., description="Entity ID"),
    note_data: EntityNoteCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new note for an entity.
    
    Only users assigned to the project or entity can create notes.
    Notes are immutable once created.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
        note_data: Note content
        
    Returns:
        Created note with creator information
        
    Raises:
        400: Invalid entity type or empty note
        403: Access denied
        404: Entity not found
    """
    # Validate entity type
    valid_types = ['Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask', 'Bug']
    entity_type_capitalized = entity_type.capitalize()
    
    # Handle special cases
    if entity_type.lower() == 'usecase':
        entity_type_capitalized = 'UseCase'
    elif entity_type.lower() == 'userstory':
        entity_type_capitalized = 'UserStory'
    
    if entity_type_capitalized not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate note text
    if not note_data.note_text or not note_data.note_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note text cannot be empty"
        )
    
    # Verify user has access to the entity
    # For clients, skip access verification as all authenticated users can access
    if entity_type_capitalized != 'Client':
        service = HierarchyService(db)
        try:
            entity_uuid = UUID(entity_id) if len(entity_id) > 20 else entity_id
            await service._verify_entity_access(entity_type.lower(), entity_uuid, current_user)
        except Exception as e:
            logger.log_system(
                level="warning",
                message=f"Access denied for user {current_user.id} to create note on {entity_type} {entity_id}",
                error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this entity"
            )
    
    # Create the note
    from app.crud.crud_entity_note import entity_note as crud_entity_note
    
    note_create = EntityNoteCreate(
        entity_type=entity_type_capitalized,
        entity_id=entity_id,
        note_text=note_data.note_text.strip(),
        is_decision=note_data.is_decision or False,
        decision_status=note_data.decision_status if note_data.is_decision else None
    )
    
    new_note = await crud_entity_note.create(
        db=db,
        obj_in=note_create,
        created_by=str(current_user.id)
    )
    
    await db.commit()
    await db.refresh(new_note)
    
    # Load creator information
    await db.refresh(new_note, ['creator'])
    
    logger.log_activity(
        action="create_entity_note",
        entity_type=entity_type_capitalized,
        entity_id=entity_id,
        note_id=new_note.id,
        user_id=str(current_user.id)
    )
    
    # Return response with creator name and decision info
    return {
        "id": new_note.id,
        "entity_type": new_note.entity_type,
        "entity_id": new_note.entity_id,
        "note_text": new_note.note_text,
        "created_by": new_note.created_by,
        "created_at": new_note.created_at,
        "creator_name": new_note.creator.full_name if new_note.creator else "Unknown User",
        "creator_email": new_note.creator.email if new_note.creator else "",
        "is_decision": new_note.is_decision,
        "decision_status": new_note.decision_status if new_note.is_decision else None
    }


@router.put("/{entity_type}/{entity_id}/notes/{note_id}/decision-status", response_model=EntityNoteResponse)
async def update_decision_status(
    entity_type: str = Path(..., description="Entity type"),
    entity_id: str = Path(..., description="Entity ID"),
    note_id: str = Path(..., description="Note/Decision ID"),
    status_update: EntityNoteUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the status of a decision note.
    
    Only decisions can have their status updated.
    Regular notes cannot be modified once created.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
        note_id: ID of the note/decision
        status_update: New decision status
        
    Returns:
        Updated decision with new status
        
    Raises:
        400: Note is not a decision
        403: Access denied
        404: Note not found
    """
    # Validate entity type
    valid_types = ['Client', 'Program', 'Project', 'UseCase', 'UserStory', 'Task', 'Subtask', 'Bug']
    entity_type_capitalized = entity_type.capitalize()
    
    # Handle special cases
    if entity_type.lower() == 'usecase':
        entity_type_capitalized = 'UseCase'
    elif entity_type.lower() == 'userstory':
        entity_type_capitalized = 'UserStory'
    
    if entity_type_capitalized not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Get the note
    query = select(EntityNote).options(
        joinedload(EntityNote.creator)
    ).where(
        EntityNote.id == note_id,
        EntityNote.entity_type == entity_type_capitalized,
        EntityNote.entity_id == entity_id
    )
    
    result = await db.execute(query)
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    # Verify it's a decision
    if not note.is_decision:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only decisions can have their status updated"
        )
    
    # Verify user has access to the entity
    if entity_type_capitalized != 'Client':
        service = HierarchyService(db)
        try:
            entity_uuid = UUID(entity_id) if len(entity_id) > 20 else entity_id
            await service._verify_entity_access(entity_type.lower(), entity_uuid, current_user)
        except Exception as e:
            logger.log_system(
                level="warning",
                message=f"Access denied for user {current_user.id} to update decision on {entity_type} {entity_id}",
                error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this entity"
            )
    
    # Update decision status
    note.decision_status = status_update.decision_status
    
    await db.commit()
    await db.refresh(note)
    
    logger.log_activity(
        action="update_decision_status",
        entity_type=entity_type_capitalized,
        entity_id=entity_id,
        note_id=note_id,
        new_status=status_update.decision_status,
        user_id=str(current_user.id)
    )
    
    # Return updated decision
    return {
        "id": note.id,
        "entity_type": note.entity_type,
        "entity_id": note.entity_id,
        "note_text": note.note_text,
        "created_by": note.created_by,
        "created_at": note.created_at,
        "creator_name": note.creator.full_name if note.creator else "Unknown User",
        "creator_email": note.creator.email if note.creator else "",
        "is_decision": note.is_decision,
        "decision_status": note.decision_status
    }

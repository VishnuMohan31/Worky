"""
ADHOC Notes endpoints for the Worky API.

This module provides endpoints for managing standalone sticky notes in the TODO feature.
ADHOC notes are personal notes that are not linked to any tasks or subtasks.
Users can create, update, delete, and reorder their ADHOC notes.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.schemas.todo import (
    AdhocNoteCreate,
    AdhocNoteUpdate,
    AdhocNoteResponse,
    AdhocNoteList,
    ReorderAdhocNoteRequest
)
from app.crud.crud_todo import adhoc_note as crud_adhoc_note
from app.core.security import get_current_user
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/adhoc-notes", response_model=AdhocNoteList)
async def get_adhoc_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get ADHOC notes for the authenticated user.
    
    Notes are returned ordered by position for display in the ADHOC pane.
    Only the user's own notes are returned (ADHOC notes are always private).
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of ADHOC notes ordered by position
    """
    # Fetch ADHOC notes for the user
    notes = await crud_adhoc_note.get_by_user(
        db=db,
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )
    
    logger.log_activity(
        action="get_adhoc_notes",
        user_id=str(current_user.id),
        notes_count=len(notes)
    )
    
    return {
        "notes": notes,
        "total": len(notes)
    }


@router.post("/adhoc-notes", response_model=AdhocNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_adhoc_note(
    note_data: AdhocNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new ADHOC note for the authenticated user.
    
    ADHOC notes are standalone sticky notes that are not linked to tasks or subtasks.
    The position is automatically assigned based on existing notes.
    
    Args:
        note_data: ADHOC note data including title, content, and color
        
    Returns:
        Created ADHOC note
        
    Raises:
        400: Invalid input data
    """
    # Create the ADHOC note
    new_note = await crud_adhoc_note.create(
        db=db,
        obj_in=note_data,
        user_id=str(current_user.id)
    )
    
    logger.log_activity(
        action="create_adhoc_note",
        user_id=str(current_user.id),
        note_id=str(new_note.id)
    )
    
    return new_note


@router.put("/adhoc-notes/{note_id}", response_model=AdhocNoteResponse)
async def update_adhoc_note(
    note_id: str = Path(..., description="ADHOC note ID"),
    note_data: AdhocNoteUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing ADHOC note.
    
    Only the owner of the ADHOC note can update it.
    
    Args:
        note_id: UUID of the ADHOC note to update
        note_data: Updated ADHOC note data
        
    Returns:
        Updated ADHOC note
        
    Raises:
        404: ADHOC note not found
        403: User is not the owner of the ADHOC note
    """
    # Get the existing ADHOC note
    existing_note = await crud_adhoc_note.get(db, id=str(note_id))
    
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADHOC note not found"
        )
    
    # Check authorization - user must be the owner
    if existing_note.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own ADHOC notes"
        )
    
    # Update the ADHOC note
    updated_note = await crud_adhoc_note.update(
        db=db,
        db_obj=existing_note,
        obj_in=note_data
    )
    
    logger.log_activity(
        action="update_adhoc_note",
        user_id=str(current_user.id),
        note_id=str(updated_note.id)
    )
    
    return updated_note


@router.delete("/adhoc-notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adhoc_note(
    note_id: str = Path(..., description="ADHOC note ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete an ADHOC note.
    
    Only the owner of the ADHOC note can delete it.
    The note is marked as deleted but not physically removed from the database.
    
    Args:
        note_id: UUID of the ADHOC note to delete
        
    Raises:
        404: ADHOC note not found
        403: User is not the owner of the ADHOC note
    """
    # Get the existing ADHOC note
    existing_note = await crud_adhoc_note.get(db, id=str(note_id))
    
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADHOC note not found"
        )
    
    # Check authorization - user must be the owner
    if existing_note.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own ADHOC notes"
        )
    
    # Soft delete the ADHOC note
    await crud_adhoc_note.remove(db=db, id=str(note_id))
    
    logger.log_activity(
        action="delete_adhoc_note",
        user_id=str(current_user.id),
        note_id=str(note_id)
    )
    
    return None


@router.patch("/adhoc-notes/{note_id}/reorder", response_model=AdhocNoteResponse)
async def reorder_adhoc_note(
    note_id: str = Path(..., description="ADHOC note ID"),
    reorder_data: ReorderAdhocNoteRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reorder an ADHOC note by updating its position.
    
    This endpoint is used when dragging and dropping ADHOC notes to reorder them.
    The position management is handled automatically - other notes are shifted
    to maintain proper ordering.
    Only the owner of the ADHOC note can reorder it.
    
    Args:
        note_id: UUID of the ADHOC note to reorder
        reorder_data: New position for the note
        
    Returns:
        Updated ADHOC note with new position
        
    Raises:
        404: ADHOC note not found
        403: User is not the owner of the ADHOC note
    """
    # Get the existing ADHOC note
    existing_note = await crud_adhoc_note.get(db, id=str(note_id))
    
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADHOC note not found"
        )
    
    # Check authorization - user must be the owner
    if existing_note.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only reorder your own ADHOC notes"
        )
    
    # Reorder the ADHOC note
    updated_note = await crud_adhoc_note.reorder(
        db=db,
        note_id=note_id,
        new_position=reorder_data.position,
        user_id=str(current_user.id)
    )
    
    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADHOC note not found"
        )
    
    logger.log_activity(
        action="reorder_adhoc_note",
        user_id=str(current_user.id),
        note_id=str(updated_note.id),
        new_position=reorder_data.position
    )
    
    return updated_note

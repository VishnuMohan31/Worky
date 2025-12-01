"""
TODO Items endpoints for the Worky API.

This module provides endpoints for managing personal TODO items with time-based organization.
Users can create, update, delete, and move TODO items between date-based panes.
TODO items can optionally be linked to tasks or subtasks for context.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.db.base import get_db
from app.models.user import User
from app.schemas.todo import (
    TodoItemCreate,
    TodoItemUpdate,
    TodoItemResponse,
    TodoItemList,
    MoveTodoItemRequest,
    LinkTodoItemRequest
)
from app.crud.crud_todo import todo_item as crud_todo_item
from app.services.todo_service import todo_service
from app.core.security import get_current_user
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/todos", response_model=TodoItemList)
async def get_todo_items(
    start_date: Optional[date] = Query(None, description="Start date for filtering (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date for filtering (inclusive)"),
    include_public: bool = Query(False, description="Include public TODO items from other users"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get TODO items for the authenticated user with optional date range filtering.
    
    By default, returns only the user's own TODO items. Set include_public=true
    to also see public TODO items from other users in the same organization.
    
    Args:
        start_date: Start date for filtering (inclusive)
        end_date: End date for filtering (inclusive)
        include_public: Whether to include public items from other users
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of TODO items with linked task/subtask information
    """
    # Fetch TODO items with date range and visibility filtering
    todo_items = await crud_todo_item.get_by_date_range(
        db=db,
        user_id=str(current_user.id),
        start_date=start_date,
        end_date=end_date,
        include_public=include_public,
        skip=skip,
        limit=limit
    )
    
    # Enrich TODO items with linked entity information
    enriched_items = []
    for item in todo_items:
        item_dict = {
            "id": item.id,
            "user_id": item.user_id,
            "title": item.title,
            "description": item.description,
            "target_date": item.target_date,
            "visibility": item.visibility,
            "linked_entity_type": item.linked_entity_type,
            "linked_entity_id": item.linked_entity_id,
            "linked_entity_info": None,
            "is_deleted": item.is_deleted,
            "created_at": item.created_at,
            "updated_at": item.updated_at
        }
        
        # Fetch linked entity info if available
        if item.linked_entity_type and item.linked_entity_id:
            if item.linked_entity_type == "task":
                linked_info = await todo_service.get_task_summary(db, item.linked_entity_id)
                item_dict["linked_entity_info"] = linked_info
            elif item.linked_entity_type == "subtask":
                linked_info = await todo_service.get_subtask_summary(db, item.linked_entity_id)
                item_dict["linked_entity_info"] = linked_info
        
        enriched_items.append(item_dict)
    
    logger.log_activity(
        action="get_todo_items",
        user_id=str(current_user.id),
        items_count=len(enriched_items),
        include_public=include_public
    )
    
    return {
        "items": enriched_items,
        "total": len(enriched_items)
    }


@router.post("/todos", response_model=TodoItemResponse, status_code=status.HTTP_201_CREATED)
async def create_todo_item(
    todo_data: TodoItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new TODO item for the authenticated user.
    
    TODO items can optionally be linked to existing tasks or subtasks.
    If linking is specified, the linked entity must exist.
    
    Args:
        todo_data: TODO item data including title, description, target_date, visibility, and optional link
        
    Returns:
        Created TODO item with linked entity information if applicable
        
    Raises:
        400: Invalid input or linked entity not found
    """
    # Validate linked entity if provided
    if todo_data.linked_entity_type and todo_data.linked_entity_id:
        exists, error_msg = await todo_service.validate_entity_exists(
            db=db,
            entity_type=todo_data.linked_entity_type,
            entity_id=todo_data.linked_entity_id
        )
        
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    
    # Create the TODO item
    new_item = await crud_todo_item.create(
        db=db,
        obj_in=todo_data,
        user_id=str(current_user.id)
    )
    
    # Prepare response with linked entity info
    item_dict = {
        "id": new_item.id,
        "user_id": new_item.user_id,
        "title": new_item.title,
        "description": new_item.description,
        "target_date": new_item.target_date,
        "visibility": new_item.visibility,
        "linked_entity_type": new_item.linked_entity_type,
        "linked_entity_id": new_item.linked_entity_id,
        "linked_entity_info": None,
        "is_deleted": new_item.is_deleted,
        "created_at": new_item.created_at,
        "updated_at": new_item.updated_at
    }
    
    # Fetch linked entity info if available
    if new_item.linked_entity_type and new_item.linked_entity_id:
        if new_item.linked_entity_type == "task":
            linked_info = await todo_service.get_task_summary(db, new_item.linked_entity_id)
            item_dict["linked_entity_info"] = linked_info
        elif new_item.linked_entity_type == "subtask":
            linked_info = await todo_service.get_subtask_summary(db, new_item.linked_entity_id)
            item_dict["linked_entity_info"] = linked_info
    
    logger.log_activity(
        action="create_todo_item",
        user_id=str(current_user.id),
        todo_id=str(new_item.id),
        linked_to=f"{new_item.linked_entity_type}:{new_item.linked_entity_id}" if new_item.linked_entity_type else None
    )
    
    return item_dict


@router.put("/todos/{todo_id}", response_model=TodoItemResponse)
async def update_todo_item(
    todo_id: str = Path(..., description="TODO item ID"),
    todo_data: TodoItemUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing TODO item.
    
    Only the owner of the TODO item can update it.
    
    Args:
        todo_id: UUID of the TODO item to update
        todo_data: Updated TODO item data
        
    Returns:
        Updated TODO item
        
    Raises:
        404: TODO item not found
        403: User is not the owner of the TODO item
    """
    # Get the existing TODO item
    existing_item = await crud_todo_item.get(db, id=str(todo_id))
    
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Check authorization - user must be the owner
    if existing_item.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own TODO items"
        )
    
    # Update the TODO item
    updated_item = await crud_todo_item.update(
        db=db,
        db_obj=existing_item,
        obj_in=todo_data
    )
    
    # Prepare response with linked entity info
    item_dict = {
        "id": updated_item.id,
        "user_id": updated_item.user_id,
        "title": updated_item.title,
        "description": updated_item.description,
        "target_date": updated_item.target_date,
        "visibility": updated_item.visibility,
        "linked_entity_type": updated_item.linked_entity_type,
        "linked_entity_id": updated_item.linked_entity_id,
        "linked_entity_info": None,
        "is_deleted": updated_item.is_deleted,
        "created_at": updated_item.created_at,
        "updated_at": updated_item.updated_at
    }
    
    # Fetch linked entity info if available
    if updated_item.linked_entity_type and updated_item.linked_entity_id:
        if updated_item.linked_entity_type == "task":
            linked_info = await todo_service.get_task_summary(db, updated_item.linked_entity_id)
            item_dict["linked_entity_info"] = linked_info
        elif updated_item.linked_entity_type == "subtask":
            linked_info = await todo_service.get_subtask_summary(db, updated_item.linked_entity_id)
            item_dict["linked_entity_info"] = linked_info
    
    logger.log_activity(
        action="update_todo_item",
        user_id=str(current_user.id),
        todo_id=str(updated_item.id)
    )
    
    return item_dict


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_item(
    todo_id: str = Path(..., description="TODO item ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a TODO item.
    
    Only the owner of the TODO item can delete it.
    The item is marked as deleted but not physically removed from the database.
    
    Args:
        todo_id: UUID of the TODO item to delete
        
    Raises:
        404: TODO item not found
        403: User is not the owner of the TODO item
    """
    # Get the existing TODO item
    existing_item = await crud_todo_item.get(db, id=str(todo_id))
    
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Check authorization - user must be the owner
    if existing_item.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own TODO items"
        )
    
    # Soft delete the TODO item
    await crud_todo_item.remove(db=db, id=str(todo_id))
    
    logger.log_activity(
        action="delete_todo_item",
        user_id=str(current_user.id),
        todo_id=str(todo_id)
    )
    
    return None


@router.patch("/todos/{todo_id}/move", response_model=TodoItemResponse)
async def move_todo_item(
    todo_id: str = Path(..., description="TODO item ID"),
    move_data: MoveTodoItemRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Move a TODO item to a different date (pane).
    
    This endpoint is used when dragging and dropping TODO items between
    time-based panes (Yesterday, Today, Tomorrow, Day After Tomorrow).
    Only the owner of the TODO item can move it.
    
    Args:
        todo_id: UUID of the TODO item to move
        move_data: New target date for the TODO item
        
    Returns:
        Updated TODO item with new target date
        
    Raises:
        404: TODO item not found
        403: User is not the owner of the TODO item
    """
    # Get the existing TODO item
    existing_item = await crud_todo_item.get(db, id=str(todo_id))
    
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Check authorization - user must be the owner
    if existing_item.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only move your own TODO items"
        )
    
    # Move the TODO item to the new date
    updated_item = await crud_todo_item.move(
        db=db,
        todo_id=todo_id,
        new_target_date=move_data.target_date
    )
    
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Prepare response with linked entity info
    item_dict = {
        "id": updated_item.id,
        "user_id": updated_item.user_id,
        "title": updated_item.title,
        "description": updated_item.description,
        "target_date": updated_item.target_date,
        "visibility": updated_item.visibility,
        "linked_entity_type": updated_item.linked_entity_type,
        "linked_entity_id": updated_item.linked_entity_id,
        "linked_entity_info": None,
        "is_deleted": updated_item.is_deleted,
        "created_at": updated_item.created_at,
        "updated_at": updated_item.updated_at
    }
    
    # Fetch linked entity info if available
    if updated_item.linked_entity_type and updated_item.linked_entity_id:
        if updated_item.linked_entity_type == "task":
            linked_info = await todo_service.get_task_summary(db, updated_item.linked_entity_id)
            item_dict["linked_entity_info"] = linked_info
        elif updated_item.linked_entity_type == "subtask":
            linked_info = await todo_service.get_subtask_summary(db, updated_item.linked_entity_id)
            item_dict["linked_entity_info"] = linked_info
    
    logger.log_activity(
        action="move_todo_item",
        user_id=str(current_user.id),
        todo_id=str(updated_item.id),
        new_date=str(move_data.target_date)
    )
    
    return item_dict


@router.post("/todos/{todo_id}/link", response_model=TodoItemResponse)
async def link_todo_item(
    todo_id: str = Path(..., description="TODO item ID"),
    link_data: LinkTodoItemRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Link a TODO item to a task or subtask.
    
    This creates a reference from the TODO item to an existing task or subtask,
    allowing the user to see context information without leaving the TODO view.
    The linked entity must exist in the database.
    Only the owner of the TODO item can link it.
    
    Args:
        todo_id: UUID of the TODO item to link
        link_data: Entity type and ID to link to
        
    Returns:
        Updated TODO item with linked entity information
        
    Raises:
        400: Linked entity not found
        404: TODO item not found
        403: User is not the owner of the TODO item
    """
    # Get the existing TODO item
    existing_item = await crud_todo_item.get(db, id=str(todo_id))
    
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Check authorization - user must be the owner
    if existing_item.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only link your own TODO items"
        )
    
    # Validate that the linked entity exists
    exists, error_msg = await todo_service.validate_entity_exists(
        db=db,
        entity_type=link_data.entity_type,
        entity_id=link_data.entity_id
    )
    
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Link the TODO item to the entity
    updated_item = await crud_todo_item.link_entity(
        db=db,
        todo_id=todo_id,
        entity_type=link_data.entity_type,
        entity_id=link_data.entity_id
    )
    
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Prepare response with linked entity info
    item_dict = {
        "id": updated_item.id,
        "user_id": updated_item.user_id,
        "title": updated_item.title,
        "description": updated_item.description,
        "target_date": updated_item.target_date,
        "visibility": updated_item.visibility,
        "linked_entity_type": updated_item.linked_entity_type,
        "linked_entity_id": updated_item.linked_entity_id,
        "linked_entity_info": None,
        "is_deleted": updated_item.is_deleted,
        "created_at": updated_item.created_at,
        "updated_at": updated_item.updated_at
    }
    
    # Fetch linked entity info
    if updated_item.linked_entity_type == "task":
        linked_info = await todo_service.get_task_summary(db, updated_item.linked_entity_id)
        item_dict["linked_entity_info"] = linked_info
    elif updated_item.linked_entity_type == "subtask":
        linked_info = await todo_service.get_subtask_summary(db, updated_item.linked_entity_id)
        item_dict["linked_entity_info"] = linked_info
    
    logger.log_activity(
        action="link_todo_item",
        user_id=str(current_user.id),
        todo_id=str(updated_item.id),
        linked_to=f"{link_data.entity_type}:{link_data.entity_id}"
    )
    
    return item_dict


@router.delete("/todos/{todo_id}/link", response_model=TodoItemResponse)
async def unlink_todo_item(
    todo_id: str = Path(..., description="TODO item ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unlink a TODO item from its task or subtask.
    
    This removes the reference to the linked entity, making the TODO item standalone.
    Only the owner of the TODO item can unlink it.
    
    Args:
        todo_id: UUID of the TODO item to unlink
        
    Returns:
        Updated TODO item without linked entity
        
    Raises:
        404: TODO item not found
        403: User is not the owner of the TODO item
    """
    # Get the existing TODO item
    existing_item = await crud_todo_item.get(db, id=str(todo_id))
    
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Check authorization - user must be the owner
    if existing_item.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only unlink your own TODO items"
        )
    
    # Unlink the TODO item
    updated_item = await crud_todo_item.unlink_entity(
        db=db,
        todo_id=todo_id
    )
    
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    
    # Prepare response (no linked entity info)
    item_dict = {
        "id": updated_item.id,
        "user_id": updated_item.user_id,
        "title": updated_item.title,
        "description": updated_item.description,
        "target_date": updated_item.target_date,
        "visibility": updated_item.visibility,
        "linked_entity_type": None,
        "linked_entity_id": None,
        "linked_entity_info": None,
        "is_deleted": updated_item.is_deleted,
        "created_at": updated_item.created_at,
        "updated_at": updated_item.updated_at
    }
    
    logger.log_activity(
        action="unlink_todo_item",
        user_id=str(current_user.id),
        todo_id=str(updated_item.id)
    )
    
    return item_dict



@router.get("/tasks/{task_id}/summary", response_model=dict)
async def get_task_summary(
    task_id: str = Path(..., description="Task ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get read-only high-level information for a task.
    
    This endpoint provides summary information about a task for display in TODO items.
    It returns only read-only data and does not allow modifications to the task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        Task summary information including title, status, due date, and assigned user
        
    Raises:
        404: Task not found
    """
    # Fetch task summary
    task_summary = await todo_service.get_task_summary(db, task_id)
    
    if not task_summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    logger.log_activity(
        action="get_task_summary",
        user_id=str(current_user.id),
        task_id=task_id
    )
    
    return {
        "id": task_summary.id,
        "title": task_summary.title,
        "status": task_summary.status,
        "due_date": task_summary.due_date,
        "assigned_to": task_summary.assigned_to,
        "user_story_id": task_summary.parent_id
    }


@router.get("/subtasks/{subtask_id}/summary", response_model=dict)
async def get_subtask_summary(
    subtask_id: str = Path(..., description="Subtask ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get read-only high-level information for a subtask.
    
    This endpoint provides summary information about a subtask for display in TODO items.
    It returns only read-only data and does not allow modifications to the subtask.
    
    Args:
        subtask_id: ID of the subtask
        
    Returns:
        Subtask summary information including title, status, and assigned user
        
    Raises:
        404: Subtask not found
    """
    # Fetch subtask summary
    subtask_summary = await todo_service.get_subtask_summary(db, subtask_id)
    
    if not subtask_summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with id {subtask_id} not found"
        )
    
    logger.log_activity(
        action="get_subtask_summary",
        user_id=str(current_user.id),
        subtask_id=subtask_id
    )
    
    return {
        "id": subtask_summary.id,
        "title": subtask_summary.title,
        "status": subtask_summary.status,
        "assigned_to": subtask_summary.assigned_to,
        "task_id": subtask_summary.parent_id
    }

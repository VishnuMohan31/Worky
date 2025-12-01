from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import date

from app.crud.base import CRUDBase
from app.models.todo import TodoItem, AdhocNote
from app.schemas.todo import (
    TodoItemCreate,
    TodoItemUpdate,
    AdhocNoteCreate,
    AdhocNoteUpdate
)


class CRUDTodoItem(CRUDBase[TodoItem, TodoItemCreate, TodoItemUpdate]):
    """CRUD operations for TodoItem model"""
    
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TodoItem]:
        """
        Get all TODO items for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of TODO items for the user
        """
        query = select(TodoItem).where(
            and_(
                TodoItem.user_id == user_id,
                TodoItem.is_deleted == False
            )
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_public: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[TodoItem]:
        """
        Get TODO items filtered by date range and visibility.
        
        Args:
            db: Database session
            user_id: User ID of the requesting user
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            include_public: Whether to include public items from other users
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of TODO items matching the criteria
        """
        # Build visibility filter
        if include_public:
            # Include user's own items (public or private) OR public items from others
            visibility_filter = or_(
                TodoItem.user_id == user_id,
                TodoItem.visibility == "public"
            )
        else:
            # Only user's own items
            visibility_filter = TodoItem.user_id == user_id
        
        # Build base query
        query = select(TodoItem).where(
            and_(
                visibility_filter,
                TodoItem.is_deleted == False
            )
        )
        
        # Apply date range filters
        if start_date:
            query = query.where(TodoItem.target_date >= start_date)
        if end_date:
            query = query.where(TodoItem.target_date <= end_date)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: TodoItemCreate,
        user_id: str
    ) -> TodoItem:
        """
        Create a new TODO item.
        
        Args:
            db: Database session
            obj_in: TODO item data
            user_id: User ID of the owner
            
        Returns:
            Created TODO item
        """
        obj_in_data = obj_in.model_dump()
        obj_in_data["user_id"] = user_id
        
        db_obj = TodoItem(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def move(
        self,
        db: AsyncSession,
        *,
        todo_id: str,
        new_target_date: date
    ) -> Optional[TodoItem]:
        """
        Move a TODO item to a different date (pane).
        
        Args:
            db: Database session
            todo_id: TODO item ID
            new_target_date: New target date
            
        Returns:
            Updated TODO item or None if not found
        """
        todo_item = await self.get(db, id=str(todo_id))
        if not todo_item:
            return None
        
        todo_item.target_date = new_target_date
        db.add(todo_item)
        await db.commit()
        await db.refresh(todo_item)
        return todo_item
    
    async def link_entity(
        self,
        db: AsyncSession,
        *,
        todo_id: str,
        entity_type: str,
        entity_id: str
    ) -> Optional[TodoItem]:
        """
        Link a TODO item to a task or subtask.
        
        Args:
            db: Database session
            todo_id: TODO item ID
            entity_type: Type of entity ('task' or 'subtask')
            entity_id: ID of the entity to link
            
        Returns:
            Updated TODO item or None if not found
        """
        todo_item = await self.get(db, id=str(todo_id))
        if not todo_item:
            return None
        
        todo_item.linked_entity_type = entity_type
        todo_item.linked_entity_id = entity_id
        db.add(todo_item)
        await db.commit()
        await db.refresh(todo_item)
        return todo_item
    
    async def unlink_entity(
        self,
        db: AsyncSession,
        *,
        todo_id: str
    ) -> Optional[TodoItem]:
        """
        Unlink a TODO item from its task or subtask.
        
        Args:
            db: Database session
            todo_id: TODO item ID
            
        Returns:
            Updated TODO item or None if not found
        """
        todo_item = await self.get(db, id=str(todo_id))
        if not todo_item:
            return None
        
        todo_item.linked_entity_type = None
        todo_item.linked_entity_id = None
        db.add(todo_item)
        await db.commit()
        await db.refresh(todo_item)
        return todo_item


class CRUDAdhocNote(CRUDBase[AdhocNote, AdhocNoteCreate, AdhocNoteUpdate]):
    """CRUD operations for AdhocNote model"""
    
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AdhocNote]:
        """
        Get all ADHOC notes for a specific user, ordered by position.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of ADHOC notes for the user
        """
        query = select(AdhocNote).where(
            and_(
                AdhocNote.user_id == user_id,
                AdhocNote.is_deleted == False
            )
        ).order_by(AdhocNote.position).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: AdhocNoteCreate,
        user_id: str
    ) -> AdhocNote:
        """
        Create a new ADHOC note.
        
        Args:
            db: Database session
            obj_in: ADHOC note data
            user_id: User ID of the owner
            
        Returns:
            Created ADHOC note
        """
        # Get the highest position for this user
        max_position_query = select(AdhocNote.position).where(
            and_(
                AdhocNote.user_id == user_id,
                AdhocNote.is_deleted == False
            )
        ).order_by(AdhocNote.position.desc()).limit(1)
        
        result = await db.execute(max_position_query)
        max_position = result.scalar_one_or_none()
        
        # Set position to max + 1, or 0 if no notes exist
        new_position = (max_position + 1) if max_position is not None else 0
        
        obj_in_data = obj_in.model_dump()
        obj_in_data["user_id"] = user_id
        obj_in_data["position"] = new_position
        
        db_obj = AdhocNote(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def reorder(
        self,
        db: AsyncSession,
        *,
        note_id: str,
        new_position: int,
        user_id: str
    ) -> Optional[AdhocNote]:
        """
        Reorder an ADHOC note by updating its position.
        
        This method handles position management by:
        1. Moving the target note to the new position
        2. Adjusting positions of other notes to maintain order
        
        Args:
            db: Database session
            note_id: ADHOC note ID
            new_position: New position for the note
            user_id: User ID (for validation)
            
        Returns:
            Updated ADHOC note or None if not found
        """
        # Get the note to reorder
        note = await self.get(db, id=str(note_id))
        if not note or note.user_id != user_id:
            return None
        
        old_position = note.position
        
        # If position hasn't changed, return early
        if old_position == new_position:
            return note
        
        # Get all notes for this user (excluding the one being moved)
        all_notes_query = select(AdhocNote).where(
            and_(
                AdhocNote.user_id == user_id,
                AdhocNote.is_deleted == False,
                AdhocNote.id != note_id
            )
        ).order_by(AdhocNote.position)
        
        result = await db.execute(all_notes_query)
        other_notes = result.scalars().all()
        
        # Adjust positions of other notes
        if new_position > old_position:
            # Moving down: shift notes between old and new position up
            for other_note in other_notes:
                if old_position < other_note.position <= new_position:
                    other_note.position -= 1
                    db.add(other_note)
        else:
            # Moving up: shift notes between new and old position down
            for other_note in other_notes:
                if new_position <= other_note.position < old_position:
                    other_note.position += 1
                    db.add(other_note)
        
        # Update the target note's position
        note.position = new_position
        db.add(note)
        
        await db.commit()
        await db.refresh(note)
        return note


# Create singleton instances
todo_item = CRUDTodoItem(TodoItem)
adhoc_note = CRUDAdhocNote(AdhocNote)

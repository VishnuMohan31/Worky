from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Tuple

from app.models.hierarchy import Task, Subtask
from app.schemas.todo import LinkedTaskInfo


class TodoService:
    """Service for TODO-related operations including task/subtask summary fetching"""
    
    async def get_task_summary(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[LinkedTaskInfo]:
        """
        Get read-only high-level information for a task.
        
        Args:
            db: Database session
            task_id: Task ID
            
        Returns:
            LinkedTaskInfo with task summary or None if not found
        """
        query = select(Task).where(
            and_(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            return None
        
        # Get assigned user name if available
        assigned_to_name = None
        if task.assignee:
            assigned_to_name = task.assignee.name if hasattr(task.assignee, 'name') else task.assigned_to
        
        return LinkedTaskInfo(
            id=task.id,
            title=task.title,
            status=task.status,
            due_date=task.due_date,
            assigned_to=assigned_to_name,
            parent_id=task.user_story_id  # user_story_id is the parent for tasks
        )
    
    async def get_subtask_summary(
        self,
        db: AsyncSession,
        subtask_id: str
    ) -> Optional[LinkedTaskInfo]:
        """
        Get read-only high-level information for a subtask.
        
        Args:
            db: Database session
            subtask_id: Subtask ID
            
        Returns:
            LinkedTaskInfo with subtask summary or None if not found
        """
        query = select(Subtask).where(
            and_(
                Subtask.id == subtask_id,
                Subtask.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        subtask = result.scalar_one_or_none()
        
        if not subtask:
            return None
        
        # Get assigned user name if available
        assigned_to_name = None
        if subtask.assignee:
            assigned_to_name = subtask.assignee.name if hasattr(subtask.assignee, 'name') else subtask.assigned_to
        
        # Note: Subtasks don't have a due_date field, so we set it to None
        return LinkedTaskInfo(
            id=subtask.id,
            title=subtask.title,
            status=subtask.status,
            due_date=None,  # Subtasks don't have due_date in the model
            assigned_to=assigned_to_name,
            parent_id=subtask.task_id  # task_id is the parent for subtasks
        )
    
    async def validate_entity_exists(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: str
    ) -> Tuple[bool, str]:
        """
        Validate that a linked entity (task or subtask) exists.
        
        Args:
            db: Database session
            entity_type: Type of entity ('task' or 'subtask')
            entity_id: ID of the entity
            
        Returns:
            Tuple of (exists: bool, error_message: str)
        """
        if entity_type == "task":
            query = select(Task).where(
                and_(
                    Task.id == entity_id,
                    Task.is_deleted == False
                )
            )
            result = await db.execute(query)
            entity = result.scalar_one_or_none()
            
            if not entity:
                return False, f"Task with id {entity_id} not found"
            return True, ""
            
        elif entity_type == "subtask":
            query = select(Subtask).where(
                and_(
                    Subtask.id == entity_id,
                    Subtask.is_deleted == False
                )
            )
            result = await db.execute(query)
            entity = result.scalar_one_or_none()
            
            if not entity:
                return False, f"Subtask with id {entity_id} not found"
            return True, ""
        else:
            return False, f"Invalid entity_type: {entity_type}. Must be 'task' or 'subtask'"


# Create singleton instance
todo_service = TodoService()

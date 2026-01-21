"""
Task endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime

from app.db.base import get_db
from app.models.hierarchy import Task, UserStory, Usecase, Project, Program
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, parse_ddmmyyyy_date, format_date_to_ddmmyyyy
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException, ValidationException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


def convert_dates_for_db(data_dict: dict) -> dict:
    """Convert DD/MM/YYYY dates to date objects for database storage"""
    converted = data_dict.copy()
    
    for field in ['start_date', 'due_date']:
        if field in converted and converted[field]:
            try:
                converted[field] = parse_ddmmyyyy_date(converted[field])
            except ValueError:
                # If parsing fails, leave as is (will be caught by validation)
                pass
    
    return converted


def convert_dates_for_response(task) -> dict:
    """Convert date objects to DD/MM/YYYY format for response"""
    task_dict = TaskResponse.from_orm(task).dict()
    
    # Convert dates to DD/MM/YYYY format
    if task_dict.get('start_date'):
        task_dict['start_date'] = format_date_to_ddmmyyyy(task.start_date)
    if task_dict.get('due_date'):
        task_dict['due_date'] = format_date_to_ddmmyyyy(task.due_date)
    
    return task_dict


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_story_id: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tasks with optional filters."""
    
    # Select only columns that exist in the database
    # Note: sprint_id may not exist yet, so we handle it in serialization
    query = select(Task).where(Task.is_deleted == False)
    
    # Apply filters
    if user_story_id:
        query = query.where(Task.user_story_id == user_story_id)
    if assigned_to:
        query = query.where(Task.assigned_to == assigned_to)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.join(UserStory, Task.user_story_id == UserStory.id)\
                     .join(Usecase, UserStory.usecase_id == Usecase.id)\
                     .join(Project, Usecase.project_id == Project.id)\
                     .join(Program, Project.program_id == Program.id)\
                     .where(Program.client_id == current_user.client_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Convert tasks to response with DD/MM/YYYY dates
    response_list = []
    for task in tasks:
        try:
            # Convert dates to DD/MM/YYYY format for response
            task_dict = convert_dates_for_response(task)
            # Ensure sprint_id is set to None if column doesn't exist
            if not hasattr(task, 'sprint_id'):
                task_dict['sprint_id'] = None
            response_list.append(TaskResponse(**task_dict))
        except Exception as e:
            logger.error(f"Error serializing task {task.id}: {str(e)}", exc_info=True)
            raise  # Re-raise to see the actual error
    
    return response_list


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID."""
    
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise ResourceNotFoundException("Task", str(task_id))
    
    # Check access
    if current_user.role != "Admin":
        user_story_result = await db.execute(
            select(UserStory).join(Usecase).join(Project).join(Program).where(
                and_(
                    UserStory.id == task.user_story_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not user_story_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    logger.log_activity(
        action="view_task",
        entity_type="task",
        entity_id=str(task_id)
    )
    
    # Convert dates to DD/MM/YYYY format for response
    task_dict = convert_dates_for_response(task)
    return TaskResponse(**task_dict)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task."""
    
    # Verify user story exists
    user_story_result = await db.execute(
        select(UserStory).where(UserStory.id == task_data.user_story_id)
    )
    user_story = user_story_result.scalar_one_or_none()
    
    if not user_story:
        raise ResourceNotFoundException("UserStory", str(task_data.user_story_id))
    
    # Check access
    if current_user.role != "Admin":
        usecase_result = await db.execute(
            select(Usecase).join(Project).join(Program).where(
                and_(
                    Usecase.id == user_story.usecase_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not usecase_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    # Verify assigned user exists if provided
    if task_data.assigned_to:
        assignee_result = await db.execute(
            select(User).where(User.id == task_data.assigned_to)
        )
        if not assignee_result.scalar_one_or_none():
            raise ResourceNotFoundException("User", str(task_data.assigned_to))
    
    # Convert DD/MM/YYYY dates to date objects for database
    task_dict = convert_dates_for_db(task_data.dict())
    
    task = Task(
        **task_dict,
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    logger.log_activity(
        action="create_task",
        entity_type="task",
        entity_id=str(task.id),
        user_story_id=str(task.user_story_id),
        assigned_to=str(task.assigned_to) if task.assigned_to else None
    )
    
    # Convert dates back to DD/MM/YYYY format for response
    task_dict = convert_dates_for_response(task)
    return TaskResponse(**task_dict)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task with status transition tracking."""
    
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise ResourceNotFoundException("Task", str(task_id))
    
    # Check access
    if current_user.role != "Admin":
        user_story_result = await db.execute(
            select(UserStory).join(Usecase).join(Project).join(Program).where(
                and_(
                    UserStory.id == task.user_story_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not user_story_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    # Track status transitions
    old_status = task.status
    new_status = task_data.status if task_data.status else old_status
    
    # COMPLETELY DISABLE STATUS TRANSITION VALIDATION
    # Allow any status transition - no restrictions for flexible kanban workflow
    print(f"🔥 TASK UPDATE: task_id={task_id}, old_status='{old_status}', new_status='{new_status}'")
    print(f"🔥 TASK UPDATE: Validation is DISABLED - allowing transition")
    logger.info(f"Status transition: '{old_status}' -> '{new_status}' (validation disabled)")
    
    if new_status != old_status:
        # Set completed_at when transitioning to Completed
        if new_status == "Completed" and old_status != "Completed":
            task.completed_at = datetime.utcnow()
        # Clear completed_at when reopening
        elif old_status == "Completed" and new_status != "Completed":
            task.completed_at = None
        
        # Set completed_at when transitioning to Completed
        if new_status == "Completed" and old_status != "Completed":
            task.completed_at = datetime.utcnow()
        # Clear completed_at when reopening
        elif old_status == "Completed" and new_status != "Completed":
            task.completed_at = None
    
    # Verify assigned user exists if being updated
    if task_data.assigned_to:
        assignee_result = await db.execute(
            select(User).where(User.id == task_data.assigned_to)
        )
        if not assignee_result.scalar_one_or_none():
            raise ResourceNotFoundException("User", str(task_data.assigned_to))
    
    # Convert DD/MM/YYYY dates to date objects for database
    update_data = convert_dates_for_db(task_data.dict(exclude_unset=True))
    
    # Update fields
    for field, value in update_data.items():
        if field != "status":  # Status already handled above
            setattr(task, field, value)
    
    if task_data.status:
        task.status = new_status
    
    task.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(task)
    
    logger.log_activity(
        action="update_task",
        entity_type="task",
        entity_id=str(task_id),
        status_transition=f"{old_status} -> {new_status}" if old_status != new_status else None
    )
    
    # Convert dates back to DD/MM/YYYY format for response
    task_dict = convert_dates_for_response(task)
    return TaskResponse(**task_dict)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Project Manager"]))
):
    """Soft delete a task."""
    
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise ResourceNotFoundException("Task", str(task_id))
    
    # Check access
    if current_user.role != "Admin":
        user_story_result = await db.execute(
            select(UserStory).join(Usecase).join(Project).join(Program).where(
                and_(
                    UserStory.id == task.user_story_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not user_story_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    task.is_deleted = True
    task.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_task",
        entity_type="task",
        entity_id=str(task_id)
    )


@router.get("/my-tasks/", response_model=List[TaskResponse])
async def get_my_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tasks assigned to current user."""
    
    query = select(Task).where(
        and_(
            Task.assigned_to == current_user.id,
            Task.is_deleted == False
        )
    )
    
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Convert dates to DD/MM/YYYY format for response
    response_list = []
    for task in tasks:
        task_dict = convert_dates_for_response(task)
        response_list.append(TaskResponse(**task_dict))
    
    return response_list


@router.get("/{task_id}/progress", response_model=dict)
async def get_task_progress(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task progress including subtask completion."""
    
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise ResourceNotFoundException("Task", str(task_id))
    
    # Check access
    if current_user.role != "Admin":
        user_story_result = await db.execute(
            select(UserStory).join(Usecase).join(Project).join(Program).where(
                and_(
                    UserStory.id == task.user_story_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not user_story_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    # Calculate progress
    total_subtasks = len(task.subtasks)
    completed_subtasks = sum(1 for st in task.subtasks if st.status == "Done" and not st.is_deleted)
    
    progress_percentage = (completed_subtasks / total_subtasks * 100) if total_subtasks > 0 else 0
    
    # Calculate time tracking
    time_spent = float(task.actual_hours) if task.actual_hours else 0
    time_estimated = float(task.estimated_hours) if task.estimated_hours else 0
    time_remaining = max(0, time_estimated - time_spent) if time_estimated > 0 else None
    
    return {
        "task_id": str(task_id),
        "status": task.status,
        "total_subtasks": total_subtasks,
        "completed_subtasks": completed_subtasks,
        "progress_percentage": round(progress_percentage, 2),
        "time_estimated": time_estimated,
        "time_spent": time_spent,
        "time_remaining": time_remaining,
        "is_overdue": task.due_date < datetime.utcnow().date() if task.due_date and task.status != "Done" else False
    }

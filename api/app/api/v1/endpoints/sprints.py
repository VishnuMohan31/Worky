"""
Sprint management endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta

from app.db.base import get_db
from app.models.sprint import Sprint
from app.models.hierarchy import Project, Program, Task
from app.models.user import User
from app.schemas.sprint import SprintCreate, SprintUpdate, SprintResponse, SprintWithTasks
from app.services.sprint_service import SprintService
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException, ValidationException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/projects/{project_id}/sprint-default-dates")
async def get_project_sprint_default_dates(
    project_id: str = Path(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get default start and end dates for a new sprint in the project."""
    
    # Verify project exists and user has access
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    # Check access
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this project")
    
    # Get the latest sprint to calculate next sprint dates
    latest_sprint_result = await db.execute(
        select(Sprint).where(Sprint.project_id == project_id)
        .order_by(Sprint.end_date.desc())
        .limit(1)
    )
    latest_sprint = latest_sprint_result.scalar_one_or_none()
    
    # Calculate default dates based on project configuration
    sprint_length_weeks = int(project.sprint_length_weeks or "2")
    
    if latest_sprint:
        # Start the new sprint the day after the latest sprint ends
        start_date = latest_sprint.end_date + timedelta(days=1)
    else:
        # No existing sprints, start from today or next Monday
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:  # Today is Monday
            start_date = today
        else:
            start_date = today + timedelta(days=days_until_monday)
    
    # Calculate end date based on sprint length
    end_date = start_date + timedelta(weeks=sprint_length_weeks) - timedelta(days=1)
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }


@router.get("/projects/{project_id}/sprints", response_model=List[SprintWithTasks])
async def list_project_sprints(
    project_id: str = Path(..., description="Project ID"),
    include_past: bool = Query(False, description="Include past sprints"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all sprints for a project. Ensures at least 6 future sprints exist."""
    
    # Verify project exists and user has access
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    # Check access
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this project")
    
    # Note: Automatic sprint generation is disabled. Sprints must be created manually.
    # Get sprints
    sprints = await SprintService.get_project_sprints(db, project_id, include_past)
    
    # Get task counts for each sprint
    result_list = []
    for sprint in sprints:
        stats_result = await SprintService.get_sprint_with_stats(db, sprint.id)
        if stats_result:
            sprint_dict = SprintResponse.from_orm(sprint).dict()
            sprint_dict.update({
                "task_count": stats_result["total_tasks"],
                "completed_task_count": stats_result["completed_tasks"],
                "in_progress_task_count": stats_result["in_progress_tasks"],
                "todo_task_count": stats_result["todo_tasks"]
            })
            result_list.append(SprintWithTasks(**sprint_dict))
    
    return result_list


@router.get("/sprints/{sprint_id}", response_model=SprintWithTasks)
async def get_sprint(
    sprint_id: str = Path(..., description="Sprint ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a sprint with task statistics."""
    
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    
    if not sprint:
        raise ResourceNotFoundException("Sprint not found")
    
    # Verify access through project
    project_result = await db.execute(
        select(Project).where(Project.id == sprint.project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this sprint")
    
    stats_result = await SprintService.get_sprint_with_stats(db, sprint_id)
    if not stats_result:
        raise ResourceNotFoundException("Sprint not found")
    
    sprint_dict = SprintResponse.from_orm(sprint).dict()
    sprint_dict.update({
        "task_count": stats_result["total_tasks"],
        "completed_task_count": stats_result["completed_tasks"],
        "in_progress_task_count": stats_result["in_progress_tasks"],
        "todo_task_count": stats_result["todo_tasks"]
    })
    
    return SprintWithTasks(**sprint_dict)


@router.get("/sprints/{sprint_id}/tasks", response_model=List[dict])
async def get_sprint_tasks(
    sprint_id: str = Path(..., description="Sprint ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tasks assigned to a sprint."""
    
    # Verify sprint exists and access
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    
    if not sprint:
        raise ResourceNotFoundException("Sprint not found")
    
    # Verify access
    project_result = await db.execute(
        select(Project).where(Project.id == sprint.project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this sprint")
    
    # Get tasks
    tasks_result = await db.execute(
        select(Task).where(Task.sprint_id == sprint_id, Task.is_deleted == False)
    )
    tasks = tasks_result.scalars().all()
    
    # Convert to dict
    from app.schemas.task import TaskResponse
    return [TaskResponse.from_orm(task).dict() for task in tasks]


@router.post("/sprints", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint_data: SprintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Product Owner", "Architect", "Designer"]))
):
    """Create a new sprint with overlap validation."""
    
    # Verify project exists and access
    project_result = await db.execute(
        select(Project).where(Project.id == sprint_data.project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this project")
    
    # Validate dates
    if sprint_data.start_date >= sprint_data.end_date:
        raise ValidationException("Start date must be before end date")
    
    # Check for overlapping sprints
    overlapping_result = await db.execute(
        select(Sprint).where(
            Sprint.project_id == sprint_data.project_id,
            # Check if new sprint overlaps with existing sprints
            # Overlap occurs if: new_start <= existing_end AND new_end >= existing_start
            ((Sprint.start_date <= sprint_data.end_date) & (Sprint.end_date >= sprint_data.start_date))
        )
    )
    overlapping_sprints = overlapping_result.scalars().all()
    
    if overlapping_sprints:
        overlapping_ids = [s.id for s in overlapping_sprints]
        raise ValidationException(
            f"Sprint overlaps with existing sprint(s): {', '.join(overlapping_ids)}. "
            f"Please adjust the dates or delete/modify the overlapping sprint(s)."
        )
    
    # Create sprint
    sprint = Sprint(**sprint_data.dict())
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    
    logger.log_activity(
        action="create_sprint",
        entity_type="sprint",
        entity_id=sprint.id,
        project_id=sprint.project_id
    )
    
    return SprintResponse.from_orm(sprint)


@router.put("/sprints/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: str = Path(..., description="Sprint ID"),
    sprint_data: SprintUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Product Owner", "Architect", "Designer"]))
):
    """Update a sprint."""
    
    result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    
    if not sprint:
        raise ResourceNotFoundException("Sprint not found")
    
    # Verify access
    project_result = await db.execute(
        select(Project).where(Project.id == sprint.project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this sprint")
    
    # Update fields
    update_data = sprint_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sprint, field, value)
    
    await db.commit()
    await db.refresh(sprint)
    
    logger.log_activity(
        action="update_sprint",
        entity_type="sprint",
        entity_id=sprint.id,
        project_id=sprint.project_id
    )
    
    return SprintResponse.from_orm(sprint)


@router.post("/sprints/{sprint_id}/assign-task/{task_id}", status_code=status.HTTP_200_OK)
async def assign_task_to_sprint(
    sprint_id: str = Path(..., description="Sprint ID"),
    task_id: str = Path(..., description="Task ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a task to a sprint."""
    
    # Verify sprint exists
    sprint_result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = sprint_result.scalar_one_or_none()
    
    if not sprint:
        raise ResourceNotFoundException("Sprint not found")
    
    # Verify task exists
    task_result = await db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False))
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise ResourceNotFoundException("Task not found")
    
    # Verify access
    project_result = await db.execute(
        select(Project).where(Project.id == sprint.project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this sprint")
    
    # Assign task to sprint
    task.sprint_id = sprint_id
    await db.commit()
    await db.refresh(task)
    
    logger.log_activity(
        action="assign_task_to_sprint",
        entity_type="task",
        entity_id=task_id,
        sprint_id=sprint_id
    )
    
    from app.schemas.task import TaskResponse
    return TaskResponse.from_orm(task)


@router.delete("/sprints/{sprint_id}/unassign-task/{task_id}", status_code=status.HTTP_200_OK)
async def unassign_task_from_sprint(
    sprint_id: str = Path(..., description="Sprint ID"),
    task_id: str = Path(..., description="Task ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unassign a task from a sprint."""
    
    # Verify sprint exists
    sprint_result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = sprint_result.scalar_one_or_none()
    
    if not sprint:
        raise ResourceNotFoundException("Sprint not found")
    
    # Verify task exists
    task_result = await db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False))
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise ResourceNotFoundException("Task not found")
    
    if task.sprint_id != sprint_id:
        raise ValidationException("Task is not assigned to this sprint")
    
    # Verify access
    project_result = await db.execute(
        select(Project).where(Project.id == sprint.project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this sprint")
    
    # Unassign task from sprint
    task.sprint_id = None
    await db.commit()
    await db.refresh(task)
    
    logger.log_activity(
        action="unassign_task_from_sprint",
        entity_type="task",
        entity_id=task_id,
        sprint_id=sprint_id
    )
    
    from app.schemas.task import TaskResponse
    return TaskResponse.from_orm(task)


@router.delete("/sprints/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    sprint_id: str = Path(..., description="Sprint ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Product Owner", "Architect", "Designer"]))
):
    """Delete a sprint. Only allowed if no tasks are assigned to it."""
    
    # Verify sprint exists
    sprint_result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
    sprint = sprint_result.scalar_one_or_none()
    
    if not sprint:
        raise ResourceNotFoundException("Sprint not found")
    
    # Verify access
    project_result = await db.execute(
        select(Project).where(Project.id == sprint.project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project not found")
    
    program_result = await db.execute(
        select(Program).where(Program.id == project.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if current_user.role != "Admin" and program and program.client_id != current_user.client_id:
        raise AccessDeniedException("You don't have access to this sprint")
    
    # Check if any tasks are assigned to this sprint
    tasks_result = await db.execute(
        select(Task).where(Task.sprint_id == sprint_id, Task.is_deleted == False)
    )
    tasks = tasks_result.scalars().all()
    
    if tasks:
        task_ids = [t.id for t in tasks]
        raise ValidationException(
            f"Cannot delete sprint. {len(tasks)} task(s) are assigned to this sprint: {', '.join(task_ids[:5])}"
            f"{'...' if len(task_ids) > 5 else ''}. "
            f"Please unassign all tasks before deleting the sprint."
        )
    
    # Delete sprint
    await db.delete(sprint)
    await db.flush()  # Flush before commit to ensure deletion is processed
    await db.commit()
    
    logger.log_activity(
        action="delete_sprint",
        entity_type="sprint",
        entity_id=sprint_id,
        project_id=sprint.project_id
    )
    
    return None




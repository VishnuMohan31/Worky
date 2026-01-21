"""
Project endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.db.base import get_db
from app.models.hierarchy import Project, Program
from app.models.sprint import Sprint
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, parse_ddmmyyyy_date, format_date_to_ddmmyyyy
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger
from app.services.sprint_service import SprintService
from app.schemas.sprint import SprintWithTasks, SprintResponse
from datetime import date, timedelta

router = APIRouter()
logger = StructuredLogger(__name__)


def convert_dates_for_db(data_dict: dict) -> dict:
    """Convert DD/MM/YYYY dates to date objects for database storage"""
    converted = data_dict.copy()
    
    for field in ['start_date', 'end_date']:
        if field in converted and converted[field]:
            try:
                converted[field] = parse_ddmmyyyy_date(converted[field])
            except ValueError:
                # If parsing fails, leave as is (will be caught by validation)
                pass
    
    return converted


def convert_dates_for_response(project) -> dict:
    """Convert date objects to DD/MM/YYYY format for response"""
    project_dict = ProjectResponse.from_orm(project).dict()
    
    # Convert dates to DD/MM/YYYY format
    if project_dict.get('start_date'):
        project_dict['start_date'] = format_date_to_ddmmyyyy(project.start_date)
    if project_dict.get('end_date'):
        project_dict['end_date'] = format_date_to_ddmmyyyy(project.end_date)
    
    return project_dict


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    program_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List projects with optional filters."""
    
    query = select(Project).options(selectinload(Project.program)).join(Program).where(Project.is_deleted == False)
    
    # Apply filters
    if program_id:
        query = query.where(Project.program_id == program_id)
    if status:
        query = query.where(Project.status == status)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.where(Program.client_id == current_user.client_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    logger.log_activity(
        action="list_projects",
        entity_type="project",
        filters={"program_id": str(program_id) if program_id else None, "status": status}
    )
    
    # Build response with program name and convert dates to DD/MM/YYYY
    response_list = []
    for proj in projects:
        proj_dict = convert_dates_for_response(proj)
        proj_dict["program_name"] = proj.program.name if proj.program else None
        response_list.append(ProjectResponse(**proj_dict))
    
    return response_list


@router.get("/{project_id}/sprint-default-dates", response_model=dict)
async def get_default_sprint_dates(
    project_id: str = Path(..., description="Project ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get default sprint start and end dates based on project configuration."""
    
    # Verify project exists and access
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.is_deleted == False)
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
    
    # Get sprint configuration
    length_weeks, starting_day = await SprintService.get_or_create_sprint_config(db, project_id)
    length_weeks_int = int(length_weeks)
    
    # Get the latest sprint for this project to determine next start date
    latest_result = await db.execute(
        select(Sprint)
        .where(Sprint.project_id == project_id)
        .order_by(Sprint.end_date.desc())
        .limit(1)
    )
    latest_sprint = latest_result.scalar_one_or_none()
    
    # Determine start date for new sprint
    if latest_sprint:
        # Start from the day after the latest sprint ends
        candidate_start = latest_sprint.end_date + timedelta(days=1)
        next_start_date = max(candidate_start, date.today())
    else:
        # No sprints exist, start from today
        next_start_date = date.today()
    
    # Calculate default sprint dates
    sprint_start, sprint_end = SprintService.calculate_sprint_dates(
        next_start_date, length_weeks_int, starting_day
    )
    
    return {
        "start_date": sprint_start.isoformat(),
        "end_date": sprint_end.isoformat(),
        "sprint_length_weeks": length_weeks,
        "sprint_starting_day": starting_day
    }


@router.get("/{project_id}/sprints", response_model=List[SprintWithTasks])
async def list_project_sprints(
    project_id: str,
    include_past: bool = Query(False, description="Include past sprints"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all sprints for a project. Note: Automatic sprint generation is disabled."""
    
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


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project by ID."""
    
    result = await db.execute(
        select(Project).options(selectinload(Project.program)).where(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project", str(project_id))
    
    # Check access
    if current_user.role != "Admin":
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    logger.log_activity(
        action="view_project",
        entity_type="project",
        entity_id=str(project_id)
    )
    
    # Build response with program name and convert dates to DD/MM/YYYY
    proj_dict = convert_dates_for_response(project)
    proj_dict["program_name"] = project.program.name if project.program else None
    return ProjectResponse(**proj_dict)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Project Manager", "Architect"]))
):
    """Create a new project."""
    
    # Verify program exists
    program_result = await db.execute(
        select(Program).where(Program.id == project_data.program_id)
    )
    program = program_result.scalar_one_or_none()
    
    if not program:
        raise ResourceNotFoundException("Program", str(project_data.program_id))
    
    # Check access
    if current_user.role != "Admin" and program.client_id != current_user.client_id:
        raise AccessDeniedException()
    
    # Convert DD/MM/YYYY dates to date objects for database
    project_dict = convert_dates_for_db(project_data.dict())
    
    project = Project(
        **project_dict,
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # Reload with program relationship
    result = await db.execute(
        select(Project).options(selectinload(Project.program)).where(Project.id == project.id)
    )
    project = result.scalar_one()
    
    logger.log_activity(
        action="create_project",
        entity_type="project",
        entity_id=str(project.id),
        program_id=str(project.program_id),
        repository_url=project.repository_url
    )
    
    # Build response with program name and convert dates to DD/MM/YYYY
    proj_dict = convert_dates_for_response(project)
    proj_dict["program_name"] = project.program.name if project.program else None
    return ProjectResponse(**proj_dict)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Project Manager", "Architect"]))
):
    """Update a project."""
    
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project", str(project_id))
    
    # Check access
    if current_user.role != "Admin":
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    # Check if sprint configuration is being changed
    old_sprint_length = project.sprint_length_weeks
    old_sprint_starting_day = project.sprint_starting_day
    sprint_config_changed = False
    
    # Convert DD/MM/YYYY dates to date objects for database
    update_data = convert_dates_for_db(project_data.dict(exclude_unset=True))
    
    # Additional date validation for update case
    start_date = update_data.get('start_date', project.start_date)
    end_date = update_data.get('end_date', project.end_date)
    
    # Validate date range if both dates exist
    if start_date and end_date and end_date < start_date:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )
    
    # Check if sprint config fields are being updated
    if 'sprint_length_weeks' in update_data or 'sprint_starting_day' in update_data:
        new_sprint_length = update_data.get('sprint_length_weeks', old_sprint_length)
        new_sprint_starting_day = update_data.get('sprint_starting_day', old_sprint_starting_day)
        
        if (new_sprint_length != old_sprint_length or 
            new_sprint_starting_day != old_sprint_starting_day):
            sprint_config_changed = True
    
    # Update fields
    for field, value in update_data.items():
        setattr(project, field, value)
    
    project.updated_by = str(current_user.id)
    
    await db.commit()
    
    # If sprint configuration changed, regenerate future sprints
    if sprint_config_changed:
        from datetime import date
        
        # Regenerate future sprints with new configuration
        # This will delete all sprints starting from today and recreate them
        await SprintService.ensure_future_sprints(
            db=db,
            project_id=project_id,
            min_sprints=6,
            regenerate_from_date=date.today()
        )
        
        logger.log_activity(
            action="update_project_sprint_config",
            entity_type="project",
            entity_id=str(project_id),
            old_sprint_length=old_sprint_length,
            new_sprint_length=update_data.get('sprint_length_weeks'),
            old_sprint_starting_day=old_sprint_starting_day,
            new_sprint_starting_day=update_data.get('sprint_starting_day')
        )
    
    # Reload with program relationship
    result = await db.execute(
        select(Project).options(selectinload(Project.program)).where(Project.id == project.id)
    )
    project = result.scalar_one()
    
    logger.log_activity(
        action="update_project",
        entity_type="project",
        entity_id=str(project_id),
        repository_url=project.repository_url
    )
    
    # Build response with program name and convert dates to DD/MM/YYYY
    proj_dict = convert_dates_for_response(project)
    proj_dict["program_name"] = project.program.name if project.program else None
    return ProjectResponse(**proj_dict)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Soft delete a project."""
    
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise ResourceNotFoundException("Project", str(project_id))
    
    # Check access
    if current_user.role != "Admin":
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    project.is_deleted = True
    project.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_project",
        entity_type="project",
        entity_id=str(project_id)
    )

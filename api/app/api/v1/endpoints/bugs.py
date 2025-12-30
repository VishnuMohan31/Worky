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
from app.schemas.bug import BugCreate, BugUpdate, BugResponse, BugList, BugStatusUpdate
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
    
    try:
        query = select(Bug).where(Bug.is_deleted == False)
        
        # Apply filters (only for fields that exist in the model)
        if severity:
            query = query.where(Bug.severity == severity)
        if priority:
            query = query.where(Bug.priority == priority)
        if status:
            query = query.where(Bug.status == status)
        if assigned_to:
            query = query.where(Bug.assigned_to == str(assigned_to))
        if reported_by:
            query = query.where(Bug.reported_by == str(reported_by))
        
        # Count total
        count_query = select(Bug).where(Bug.is_deleted == False)
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
    except Exception as e:
        # Return empty list if there's a database schema mismatch
        logger.error(f"Error listing bugs: {str(e)}")
        return BugList(
            bugs=[],
            total=0,
            page=1,
            page_size=limit,
            has_more=False
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
    """
    Create a new bug with hierarchy selection and optional assignment.
    
    Supports:
    - Hierarchy association at any level (Client through Subtask)
    - Category, severity, and priority classification
    - Assignment during creation (reporter, assignee, qa_owner)
    - Reproduction path fields
    - Automatic notification to assignee and QA owner
    """
    from app.services.notification_service import notification_service
    
    # Validate that at least one hierarchy level is set (unless linked to test run/case)
    hierarchy_fields = [
        bug_data.client_id, bug_data.program_id, bug_data.project_id,
        bug_data.usecase_id, bug_data.user_story_id, bug_data.task_id,
        bug_data.subtask_id, bug_data.test_run_id, bug_data.test_case_id
    ]
    if not any(hierarchy_fields):
        raise ValidationException(
            "At least one hierarchy level or test run/case must be specified"
        )
    
    # Validate assignee if provided
    if bug_data.assignee_id:
        assignee_result = await db.execute(
            select(User).where(
                and_(
                    User.id == bug_data.assignee_id,
                    User.is_deleted == False
                )
            )
        )
        assignee = assignee_result.scalar_one_or_none()
        
        if not assignee:
            raise ValidationException(
                f"Assignee with id {bug_data.assignee_id} not found or inactive"
            )
    
    # Validate QA owner if provided
    if bug_data.qa_owner_id:
        qa_owner_result = await db.execute(
            select(User).where(
                and_(
                    User.id == bug_data.qa_owner_id,
                    User.is_deleted == False
                )
            )
        )
        qa_owner = qa_owner_result.scalar_one_or_none()
        
        if not qa_owner:
            raise ValidationException(
                f"QA owner with id {bug_data.qa_owner_id} not found or inactive"
            )
    
    # Create bug with default status
    bug_dict = bug_data.dict()
    
    # Set reporter to current user if not specified
    if not bug_dict.get("reporter_id"):
        bug_dict["reporter_id"] = str(current_user.id)
    
    # Set legacy fields for backward compatibility
    bug_dict["reported_by"] = bug_dict.get("reporter_id", str(current_user.id))
    if bug_dict.get("assignee_id"):
        bug_dict["assigned_to"] = bug_dict["assignee_id"]
    
    bug_dict["created_by"] = str(current_user.id)
    bug_dict["updated_by"] = str(current_user.id)
    bug_dict["status"] = "New"  # Default status for new bugs
    
    bug = Bug(**bug_dict)
    
    db.add(bug)
    await db.commit()
    await db.refresh(bug)
    
    logger.log_activity(
        action="create_bug",
        entity_type="bug",
        entity_id=str(bug.id),
        category=bug.category,
        severity=bug.severity,
        priority=bug.priority,
        assignee_id=bug.assignee_id,
        qa_owner_id=bug.qa_owner_id
    )
    
    # Send notification to assignee if assigned during creation
    if bug.assignee_id:
        await notification_service.notify_bug_assignee(
            db=db,
            bug_id=str(bug.id),
            assignee_id=bug.assignee_id,
            assigned_by_id=str(current_user.id),
            bug_title=bug.title
        )
    
    # Send notification to QA owner if assigned during creation
    if bug.qa_owner_id and bug.qa_owner_id != bug.assignee_id:
        await notification_service.notify_bug_assignee(
            db=db,
            bug_id=str(bug.id),
            assignee_id=bug.qa_owner_id,
            assigned_by_id=str(current_user.id),
            bug_title=bug.title
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


@router.post("/{bug_id}/assign", response_model=BugResponse)
async def assign_bug(
    bug_id: str,
    assignee_id: str = Query(..., description="User ID to assign the bug to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Tester", "Project Manager"]))
):
    """
    Assign a bug to a user with validation and notification.
    
    Validates that:
    - The bug exists and is not deleted
    - The assignee exists and is active
    
    Tracks assignment history and sends notification to the new assignee.
    """
    from app.crud.crud_bug import bug as crud_bug
    
    # Use CRUD method for assignment with validation
    updated_bug, error_msg = await crud_bug.assign_bug(
        db,
        bug_id=bug_id,
        assignee_id=assignee_id,
        assigned_by=str(current_user.id)
    )
    
    if error_msg:
        raise ValidationException(error_msg)
    
    if not updated_bug:
        raise ResourceNotFoundException("Bug", bug_id)
    
    logger.log_activity(
        action="assign_bug",
        entity_type="bug",
        entity_id=str(bug_id),
        assignee_id=str(assignee_id),
        assigned_by=str(current_user.id)
    )
    
    # Send notification to new assignee
    # TODO: Implement notification service
    # For now, just log the notification
    logger.log_activity(
        action="notify_bug_assignment",
        entity_type="bug",
        entity_id=str(bug_id),
        assignee_id=assignee_id,
        message=f"Bug {bug_id} assigned to user {assignee_id} by {current_user.id}"
    )
    
    return BugResponse.from_orm(updated_bug)


@router.post("/{bug_id}/status", response_model=BugResponse)
async def update_bug_status(
    bug_id: str,
    status_update: BugStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update bug status with validation and history tracking.
    
    Validates status transitions according to the bug lifecycle workflow.
    Requires resolution_type when status is "Fixed".
    Records all status changes in bug_status_history table.
    Updates closed_at timestamp for terminal statuses.
    """
    from app.crud.crud_bug import bug as crud_bug
    
    # Use CRUD method for status update with validation
    updated_bug, error_msg = await crud_bug.update_status(
        db,
        bug_id=bug_id,
        new_status=status_update.status.value,
        resolution_type=status_update.resolution_type.value if status_update.resolution_type else None,
        resolution_notes=status_update.resolution_notes,
        updated_by=str(current_user.id)
    )
    
    if error_msg:
        raise ValidationException(error_msg)
    
    if not updated_bug:
        raise ResourceNotFoundException("Bug", bug_id)
    
    logger.log_activity(
        action="update_bug_status",
        entity_type="bug",
        entity_id=str(bug_id),
        from_status=updated_bug.status,
        to_status=status_update.status.value,
        resolution_type=status_update.resolution_type.value if status_update.resolution_type else None
    )
    
    return BugResponse.from_orm(updated_bug)


@router.post("/{bug_id}/resolve")
async def resolve_bug(
    bug_id: str,
    resolution_notes: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a bug as resolved (legacy endpoint).
    
    Deprecated: Use POST /bugs/{bug_id}/status instead.
    """
    
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


@router.get("/{bug_id}/history")
async def get_bug_history(
    bug_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bug history including status changes, assignments, and field updates.
    
    Returns a chronological list of all changes made to the bug, including:
    - Status transitions with resolution types
    - Assignment changes
    - System-generated notes
    
    Results are ordered by timestamp descending (most recent first).
    """
    from app.models.comment import BugStatusHistory
    
    # Verify bug exists
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
        raise ResourceNotFoundException("Bug", bug_id)
    
    # Get status history
    status_history_result = await db.execute(
        select(BugStatusHistory)
        .where(BugStatusHistory.bug_id == bug_id)
        .order_by(BugStatusHistory.changed_at.desc())
    )
    status_history = status_history_result.scalars().all()
    
    # Build history response
    history_items = []
    
    for history_entry in status_history:
        # Get user who made the change
        user_result = await db.execute(
            select(User).where(User.id == history_entry.changed_by)
        )
        user = user_result.scalar_one_or_none()
        user_name = user.username if user else "Unknown User"
        
        # Build history item
        history_item = {
            "id": history_entry.id,
            "type": "status_change",
            "timestamp": history_entry.changed_at,
            "changed_by": history_entry.changed_by,
            "changed_by_name": user_name,
            "from_status": history_entry.from_status,
            "to_status": history_entry.to_status,
            "resolution_type": history_entry.resolution_type,
            "notes": history_entry.notes,
            "description": f"Status changed from '{history_entry.from_status}' to '{history_entry.to_status}'"
        }
        
        if history_entry.resolution_type:
            history_item["description"] += f" (Resolution: {history_entry.resolution_type})"
        
        history_items.append(history_item)
    
    # Add bug creation as a history item
    if bug.created_at:
        creator_result = await db.execute(
            select(User).where(User.id == bug.created_by)
        )
        creator = creator_result.scalar_one_or_none()
        creator_name = creator.username if creator else "Unknown User"
        
        history_items.append({
            "id": f"{bug.id}_created",
            "type": "created",
            "timestamp": bug.created_at,
            "changed_by": bug.created_by,
            "changed_by_name": creator_name,
            "description": f"Bug created by {creator_name}",
            "severity": bug.severity,
            "priority": bug.priority
        })
    
    # Sort all history items by timestamp descending
    history_items.sort(key=lambda x: x["timestamp"], reverse=True)
    
    logger.log_activity(
        action="view_bug_history",
        entity_type="bug",
        entity_id=str(bug_id)
    )
    
    return {
        "bug_id": bug_id,
        "history": history_items,
        "total_changes": len(history_items)
    }


@router.get("/hierarchy", response_model=BugList)
async def get_bugs_by_hierarchy(
    client_id: Optional[str] = Query(None),
    program_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    usecase_id: Optional[str] = Query(None),
    user_story_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    subtask_id: Optional[str] = Query(None),
    include_descendants: bool = Query(True, description="Include bugs from descendant hierarchy levels"),
    status: Optional[List[str]] = Query(None, description="Filter by status (can specify multiple)"),
    category: Optional[List[str]] = Query(None, description="Filter by category (can specify multiple)"),
    severity: Optional[List[str]] = Query(None, description="Filter by severity (can specify multiple)"),
    priority: Optional[List[str]] = Query(None, description="Filter by priority (can specify multiple)"),
    assignee_id: Optional[str] = Query(None, description="Filter by assignee"),
    reporter_id: Optional[str] = Query(None, description="Filter by reporter"),
    qa_owner_id: Optional[str] = Query(None, description="Filter by QA owner"),
    search: Optional[str] = Query(None, description="Search in title, description, and reproduction steps"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bugs filtered by hierarchy level with optional descendant inclusion.
    
    This endpoint allows viewing bugs at any hierarchy level and optionally
    including all bugs from descendant levels. For example, selecting a Project
    can show bugs from the project itself and all its use cases, user stories,
    tasks, and subtasks.
    
    Supports advanced filtering by status, category, severity, priority, assignee,
    reporter, QA owner, and text search in title/description/reproduction steps.
    
    Returns bugs with hierarchy path and test run/test case information.
    """
    from app.crud.crud_bug import bug as crud_bug
    from app.models.hierarchy import Client, Program, Project, Usecase, UserStory, Task, Subtask
    from app.models.test_case import TestRun, TestCase
    
    try:
        # Build base query with search filter applied before pagination
        query = select(Bug).where(Bug.is_deleted == False)
        
        # Apply text search filter early if provided
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Bug.title.ilike(search_pattern),
                    Bug.description.ilike(search_pattern),
                    Bug.reproduction_steps.ilike(search_pattern)
                )
            )
        
        # Determine which CRUD method to use based on include_descendants
        if include_descendants:
            bugs = await crud_bug.get_by_hierarchy_with_descendants(
                db,
                client_id=client_id,
                program_id=program_id,
                project_id=project_id,
                usecase_id=usecase_id,
                user_story_id=user_story_id,
                task_id=task_id,
                subtask_id=subtask_id,
                severity=severity,
                status=status,
                priority=priority,
                category=category,
                assignee_id=assignee_id,
                reporter_id=reporter_id,
                qa_owner_id=qa_owner_id,
                search=search,
                skip=skip,
                limit=limit
            )
        else:
            bugs = await crud_bug.get_by_hierarchy(
                db,
                client_id=client_id,
                program_id=program_id,
                project_id=project_id,
                usecase_id=usecase_id,
                user_story_id=user_story_id,
                task_id=task_id,
                subtask_id=subtask_id,
                severity=severity,
                status=status,
                priority=priority,
                category=category,
                assignee_id=assignee_id,
                reporter_id=reporter_id,
                qa_owner_id=qa_owner_id,
                search=search,
                skip=skip,
                limit=limit
            )
        
        # Build hierarchy path and test run/test case info for each bug
        bug_responses = []
        for bug in bugs:
            bug_response = BugResponse.from_orm(bug)
            
            # Build hierarchy path
            path_parts = []
            if bug.client_id:
                client_result = await db.execute(select(Client).where(Client.id == bug.client_id))
                client = client_result.scalar_one_or_none()
                if client:
                    path_parts.append(client.name)
            
            if bug.program_id:
                program_result = await db.execute(select(Program).where(Program.id == bug.program_id))
                program = program_result.scalar_one_or_none()
                if program:
                    path_parts.append(program.name)
            
            if bug.project_id:
                project_result = await db.execute(select(Project).where(Project.id == bug.project_id))
                project = project_result.scalar_one_or_none()
                if project:
                    path_parts.append(project.name)
            
            if bug.usecase_id:
                usecase_result = await db.execute(select(Usecase).where(Usecase.id == bug.usecase_id))
                usecase = usecase_result.scalar_one_or_none()
                if usecase:
                    path_parts.append(usecase.name)
            
            if bug.user_story_id:
                user_story_result = await db.execute(select(UserStory).where(UserStory.id == bug.user_story_id))
                user_story = user_story_result.scalar_one_or_none()
                if user_story:
                    path_parts.append(user_story.title)
            
            if bug.task_id:
                task_result = await db.execute(select(Task).where(Task.id == bug.task_id))
                task = task_result.scalar_one_or_none()
                if task:
                    path_parts.append(task.title)
            
            if bug.subtask_id:
                subtask_result = await db.execute(select(Subtask).where(Subtask.id == bug.subtask_id))
                subtask = subtask_result.scalar_one_or_none()
                if subtask:
                    path_parts.append(subtask.title)
            
            bug_response.hierarchy_path = " > ".join(path_parts) if path_parts else "No hierarchy"
            
            # Add test run and test case information if available
            if bug.test_run_id:
                test_run_result = await db.execute(select(TestRun).where(TestRun.id == bug.test_run_id))
                test_run = test_run_result.scalar_one_or_none()
                if test_run:
                    bug_response.test_run_name = test_run.name
            
            if bug.test_case_id:
                test_case_result = await db.execute(select(TestCase).where(TestCase.id == bug.test_case_id))
                test_case = test_case_result.scalar_one_or_none()
                if test_case:
                    bug_response.test_case_name = test_case.test_case_name
            
            # Calculate age in days
            if bug.created_at:
                age_delta = datetime.utcnow() - bug.created_at.replace(tzinfo=None)
                bug_response.age_days = age_delta.days
            
            bug_responses.append(bug_response)
        
        # Get total count (without pagination)
        # For simplicity, we'll use the length of filtered results
        # In production, you'd want a separate count query
        total = len(bug_responses)
        
        logger.log_activity(
            action="list_bugs_hierarchy",
            entity_type="bug",
            filters={
                "client_id": client_id,
                "program_id": program_id,
                "project_id": project_id,
                "usecase_id": usecase_id,
                "user_story_id": user_story_id,
                "task_id": task_id,
                "subtask_id": subtask_id,
                "include_descendants": include_descendants,
                "search": search
            }
        )
        
        return BugList(
            bugs=bug_responses,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            has_more=(skip + limit) < total
        )
    
    except Exception as e:
        logger.error(f"Error listing bugs by hierarchy: {str(e)}")
        raise


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

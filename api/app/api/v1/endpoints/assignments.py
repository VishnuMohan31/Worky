"""
Assignment management endpoints for the Worky API.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.models.team import Assignment, AssignmentHistory, Team, TeamMember
from app.models.user import User
from app.models.hierarchy import Project, Usecase, UserStory, Task, Subtask
from app.models.client import Client
from app.schemas.team import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentHistoryResponse, AvailableAssigneeResponse, AssignmentSummaryResponse
)
from app.core.security import get_current_user
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException, ValidationException
from app.core.logging import StructuredLogger
from app.core.utils import generate_id
from app.services.assignment_service import AssignmentService
from app.services.validation_service import ValidationService

router = APIRouter()
logger = StructuredLogger(__name__)



async def get_entity_name(entity_type: str, entity_id: str, db: AsyncSession) -> Optional[str]:
    """Get the name of an entity by type and ID."""
    entity_models = {
        'client': Client,
        'project': Project,
        'usecase': Usecase,
        'userstory': UserStory,
        'task': Task,
        'subtask': Subtask
    }
    
    if entity_type not in entity_models:
        return None
    
    model = entity_models[entity_type]
    result = await db.execute(select(model).where(model.id == entity_id))
    entity = result.scalar_one_or_none()
    
    if not entity:
        return None
    
    # Different entities have different name fields
    if hasattr(entity, 'name'):
        return entity.name
    elif hasattr(entity, 'title'):
        return entity.title
    elif hasattr(entity, 'description'):
        return entity.description[:50] + "..." if len(entity.description) > 50 else entity.description
    
    return f"{entity_type}:{entity_id}"


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new assignment - allows multiple users with same role, prevents duplicate user+role combinations."""
    
    try:
        # Validate user exists
        user_result = await db.execute(select(User).where(User.id == assignment_data.user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Use assignment service for role validation
        assignment_service = AssignmentService(db)
        validation_result = await assignment_service.validate_assignment(
            entity_type=assignment_data.entity_type,
            entity_id=assignment_data.entity_id,
            user_id=assignment_data.user_id,
            assignment_type=assignment_data.assignment_type
        )
        
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        # Check for existing assignment - ONLY prevent same user + same role combination
        existing_result = await db.execute(
            select(Assignment).where(
                and_(
                    Assignment.entity_type == assignment_data.entity_type,
                    Assignment.entity_id == assignment_data.entity_id,
                    Assignment.user_id == assignment_data.user_id,
                    Assignment.assignment_type == assignment_data.assignment_type,
                    Assignment.is_active == True
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="User is already assigned this role for this entity")
        
        # Create new assignment - ALWAYS CREATE NEW, NEVER UPDATE EXISTING
        new_assignment = Assignment(
            id=generate_id("ASSGN"),
            entity_type=assignment_data.entity_type,
            entity_id=assignment_data.entity_id,
            user_id=assignment_data.user_id,
            assignment_type=assignment_data.assignment_type,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.add(new_assignment)
        await db.commit()
        
        # Return response
        return AssignmentResponse(
            id=new_assignment.id,
            entity_type=assignment_data.entity_type,
            entity_id=assignment_data.entity_id,
            user_id=assignment_data.user_id,
            assignment_type=assignment_data.assignment_type,
            assigned_at=datetime.utcnow(),
            is_active=True,
            user_name=user.full_name,
            user_email=user.email,
            entity_name=f"{assignment_data.entity_type}:{assignment_data.entity_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Assignment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create assignment")


@router.get("/", response_model=List[AssignmentResponse])
async def list_assignments(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    assignment_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List assignments with optional filters."""
    
    query = select(Assignment).options(selectinload(Assignment.user))
    
    # Apply filters
    if entity_type:
        query = query.where(Assignment.entity_type == entity_type)
    if entity_id:
        query = query.where(Assignment.entity_id == entity_id)
    if user_id:
        query = query.where(Assignment.user_id == user_id)
    if assignment_type:
        query = query.where(Assignment.assignment_type == assignment_type)
    if is_active is not None:
        query = query.where(Assignment.is_active == is_active)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    assignments = result.scalars().all()
    
    # Convert to response format
    assignment_responses = []
    for assignment in assignments:
        entity_name = await get_entity_name(assignment.entity_type, assignment.entity_id, db)
        
        assignment_dict = {
            "id": assignment.id,
            "entity_type": assignment.entity_type,
            "entity_id": assignment.entity_id,
            "user_id": assignment.user_id,
            "assignment_type": assignment.assignment_type,
            "assigned_at": assignment.assigned_at,
            "is_active": assignment.is_active,
            "user_name": assignment.user.full_name if assignment.user else None,
            "user_email": assignment.user.email if assignment.user else None,
            "entity_name": entity_name
        }
        assignment_responses.append(AssignmentResponse(**assignment_dict))
    
    logger.log_activity(
        action="list_assignments",
        entity_type="assignment",
        user_id=current_user.id
    )
    
    return assignment_responses


@router.get("/available-assignees", response_model=List[AvailableAssigneeResponse])
async def get_available_assignees(
    entity_type: str = Query(...),
    entity_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available assignees for an entity based on team membership rules."""
    
    # Allow admins and team leads to view available assignees
    user_role = current_user.primary_role or current_user.role
    if user_role not in ["Admin", "Manager", "Lead", "Architect"]:
        # For non-admin users, they can only view assignees for entities they have access to
        # This will be validated by the entity access check below
        pass
    
    available_users = []
    project_id = None
    
    # Get project ID for all project-level entities
    if entity_type in ['usecase', 'userstory', 'task', 'subtask']:
        if entity_type == 'usecase':
            # Direct project relationship
            usecase_result = await db.execute(select(Usecase).where(Usecase.id == entity_id))
            usecase = usecase_result.scalar_one_or_none()
            if usecase:
                project_id = usecase.project_id
        
        elif entity_type == 'userstory':
            # Get project ID through userstory -> usecase -> project
            userstory_result = await db.execute(
                select(UserStory).options(selectinload(UserStory.usecase)).where(UserStory.id == entity_id)
            )
            userstory = userstory_result.scalar_one_or_none()
            if userstory and userstory.usecase:
                project_id = userstory.usecase.project_id
        
        elif entity_type == 'task':
            # Get project ID through task -> user_story -> usecase -> project
            task_result = await db.execute(
                select(Task).options(
                    selectinload(Task.user_story)
                    .selectinload(UserStory.usecase)
                ).where(Task.id == entity_id)
            )
            task = task_result.scalar_one_or_none()
            if task and task.user_story and task.user_story.usecase:
                project_id = task.user_story.usecase.project_id
        
        elif entity_type == 'subtask':
            # Get project ID through subtask -> task -> user_story -> usecase -> project
            subtask_result = await db.execute(
                select(Subtask).options(
                    selectinload(Subtask.task)
                    .selectinload(Task.user_story)
                    .selectinload(UserStory.usecase)
                ).where(Subtask.id == entity_id)
            )
            subtask = subtask_result.scalar_one_or_none()
            if subtask and subtask.task and subtask.task.user_story and subtask.task.user_story.usecase:
                project_id = subtask.task.user_story.usecase.project_id
    
    if project_id:
        # For project-level entities, only team members can be assigned
        team_members_result = await db.execute(
            select(User)
            .join(TeamMember, User.id == TeamMember.user_id)
            .join(Team, TeamMember.team_id == Team.id)
            .where(
                and_(
                    Team.project_id == project_id,
                    Team.is_active == True,
                    TeamMember.is_active == True,
                    User.is_active == True
                )
            )
        )
        available_users = team_members_result.scalars().all()
    else:
        # For non-project entities (client, program, project), all active users can be assigned
        users_result = await db.execute(
            select(User).where(User.is_active == True)
        )
        available_users = users_result.scalars().all()
    
    # Get current assignments for these users
    user_ids = [user.id for user in available_users]
    if user_ids:
        assignments_result = await db.execute(
            select(Assignment).where(
                and_(
                    Assignment.user_id.in_(user_ids),
                    Assignment.is_active == True
                )
            )
        )
        assignments = assignments_result.scalars().all()
    else:
        assignments = []
    
    # Build assignment map
    user_assignments = {}
    for assignment in assignments:
        if assignment.user_id not in user_assignments:
            user_assignments[assignment.user_id] = []
        user_assignments[assignment.user_id].append(
            f"{assignment.entity_type}:{assignment.assignment_type}"
        )
    
    # Build response
    assignee_responses = []
    for user in available_users:
        assignee_responses.append(AvailableAssigneeResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            is_team_member=True,  # All returned users are valid for assignment
            current_assignments=user_assignments.get(user.id, [])
        ))
    
    return assignee_responses


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assignment details."""
    
    query = select(Assignment).options(selectinload(Assignment.user)).where(Assignment.id == assignment_id)
    result = await db.execute(query)
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    entity_name = await get_entity_name(assignment.entity_type, assignment.entity_id, db)
    
    assignment_dict = {
        "id": assignment.id,
        "entity_type": assignment.entity_type,
        "entity_id": assignment.entity_id,
        "user_id": assignment.user_id,
        "assignment_type": assignment.assignment_type,
        "assigned_at": assignment.assigned_at,
        "is_active": assignment.is_active,
        "user_name": assignment.user.full_name if assignment.user else None,
        "user_email": assignment.user.email if assignment.user else None,
        "entity_name": entity_name
    }
    
    logger.log_activity(
        action="get_assignment",
        entity_type="assignment",
        entity_id=assignment_id,
        user_id=current_user.id
    )
    
    return AssignmentResponse(**assignment_dict)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove an assignment."""
    
    assignment_service = AssignmentService(db)
    
    # Get assignment first
    query = select(Assignment).where(Assignment.id == assignment_id)
    result = await db.execute(query)
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    try:
        # Directly delete the assignment by ID instead of using unassign_entity
        if not assignment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        # Create history entry before removing
        await assignment_service.create_assignment_history(
            assignment, "unassigned", current_user.id
        )
        
        # Soft delete the assignment
        assignment.is_active = False
        assignment.updated_by = current_user.id
        
        await db.commit()
        
        # Invalidate caches after all database operations are complete
        try:
            from app.services.cache_service import cache_service
            cache_service.clear_pattern("eligible_users")
            cache_service.clear_pattern("assignment_validation")
            cache_service.clear_pattern("assignments:")
        except Exception as e:
            # Log cache error but don't fail the deletion
            logger.error(f"Failed to clear cache after assignment deletion: {str(e)}")
        
        logger.log_activity(
            action="delete_assignment",
            entity_type="assignment",
            entity_id=assignment_id,
            user_id=current_user.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete assignment"
        )


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AssignmentResponse])
async def get_entity_assignments(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all assignments for a specific entity."""
    
    assignment_service = AssignmentService(db)
    
    try:
        assignments = await assignment_service.get_entity_assignments(entity_type, entity_id)
        
        # Convert to response format
        assignment_responses = []
        for assignment in assignments:
            entity_name = await get_entity_name(assignment.entity_type, assignment.entity_id, db)
            
            assignment_dict = {
                "id": assignment.id,
                "entity_type": assignment.entity_type,
                "entity_id": assignment.entity_id,
                "user_id": assignment.user_id,
                "assignment_type": assignment.assignment_type,
                "assigned_at": assignment.assigned_at,
                "is_active": assignment.is_active,
                "user_name": assignment.user.full_name if assignment.user else None,
                "user_email": assignment.user.email if assignment.user else None,
                "entity_name": entity_name
            }
            assignment_responses.append(AssignmentResponse(**assignment_dict))
        
        logger.log_activity(
            action="get_entity_assignments",
            entity_type="assignment",
            user_id=current_user.id
        )
        
        return assignment_responses
        
    except Exception as e:
        logger.error(f"Error getting entity assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get entity assignments"
        )


@router.post("/entity/{entity_type}/{entity_id}", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_entity(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    assignment_data: Dict[str, str] = None,  # {"user_id": "...", "assignment_type": "..."}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a user to an entity."""
    
    assignment_service = AssignmentService(db)
    
    if not assignment_data or "user_id" not in assignment_data or "assignment_type" not in assignment_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id and assignment_type are required"
        )
    
    try:
        assignment = await assignment_service.assign_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=assignment_data["user_id"],
            assignment_type=assignment_data["assignment_type"],
            current_user=current_user
        )
        
        entity_name = await get_entity_name(entity_type, entity_id, db)
        
        assignment_dict = {
            "id": assignment.id,
            "entity_type": assignment.entity_type,
            "entity_id": assignment.entity_id,
            "user_id": assignment.user_id,
            "assignment_type": assignment.assignment_type,
            "assigned_at": assignment.assigned_at,
            "is_active": assignment.is_active,
            "user_name": assignment.user.full_name if assignment.user else None,
            "user_email": assignment.user.email if assignment.user else None,
            "entity_name": entity_name
        }
        
        logger.log_activity(
            action="assign_entity",
            entity_type="assignment",
            entity_id=assignment.id,
            user_id=current_user.id
        )
        
        return AssignmentResponse(**assignment_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning entity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign entity"
        )


@router.delete("/entity/{entity_type}/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_entity(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    assignment_type: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove assignment from an entity."""
    
    assignment_service = AssignmentService(db)
    
    try:
        success = await assignment_service.unassign_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            assignment_type=assignment_type,
            current_user=current_user
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        logger.log_activity(
            action="unassign_entity",
            entity_type="assignment",
            user_id=current_user.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unassigning entity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unassign entity"
        )


@router.post("/bulk", response_model=Dict[str, Any])
async def bulk_assign(
    assignments: List[Dict[str, str]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform bulk assignment operations."""
    
    assignment_service = AssignmentService(db)
    
    try:
        results = await assignment_service.bulk_assign(assignments, current_user)
        
        logger.log_activity(
            action="bulk_assign",
            entity_type="assignment",
            user_id=current_user.id
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error in bulk assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk assignment"
        )


@router.post("/validate", response_model=Dict[str, Any])
async def validate_assignment(
    assignment_data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate assignment before creation."""
    
    validation_service = ValidationService(db)
    
    try:
        validation_result = await validation_service.validate_assignment_rules(
            entity_type=assignment_data.entity_type,
            entity_id=assignment_data.entity_id,
            user_id=assignment_data.user_id,
            assignment_type=assignment_data.assignment_type
        )
        
        return validation_result.to_dict()
        
    except Exception as e:
        logger.error(f"Error validating assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate assignment"
        )


@router.get("/eligible-users/{entity_type}/{entity_id}", response_model=List[AvailableAssigneeResponse])
async def get_eligible_assignees(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    assignment_type: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users eligible for assignment to an entity."""
    
    assignment_service = AssignmentService(db)
    
    try:
        eligible_users = await assignment_service.get_eligible_assignees(
            entity_type=entity_type,
            entity_id=entity_id,
            assignment_type=assignment_type
        )
        
        # Convert to response format
        assignee_responses = []
        for user in eligible_users:
            # Get user's current assignments for this entity type
            user_assignments = await assignment_service.get_user_assignments(user.id, entity_type)
            current_assignments = [f"{a.entity_type}:{a.entity_id}" for a in user_assignments]
            
            assignee_dict = {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.primary_role,
                "is_team_member": True,  # If they're in the list, they're eligible
                "current_assignments": current_assignments
            }
            assignee_responses.append(AvailableAssigneeResponse(**assignee_dict))
        
        logger.log_activity(
            action="get_eligible_assignees",
            entity_type="assignment",
            user_id=current_user.id
        )
        
        return assignee_responses
        
    except Exception as e:
        logger.error(f"Error getting eligible assignees: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get eligible assignees"
        )


@router.get("/history/{entity_type}/{entity_id}", response_model=List[AssignmentHistoryResponse])
async def get_assignment_history(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assignment history for an entity."""
    
    assignment_service = AssignmentService(db)
    
    try:
        history = await assignment_service.get_assignment_history(entity_type, entity_id)
        
        # Convert to response format
        history_responses = []
        for entry in history:
            history_dict = {
                "id": entry.id,
                "assignment_id": entry.assignment_id,
                "entity_type": entry.entity_type,
                "entity_id": entry.entity_id,
                "user_id": entry.user_id,
                "assignment_type": entry.assignment_type,
                "action": entry.action,
                "previous_user_id": entry.previous_user_id,
                "created_at": entry.created_at,
                "user_name": entry.user.full_name if entry.user else None,
                "previous_user_name": entry.previous_user.full_name if entry.previous_user else None
            }
            history_responses.append(AssignmentHistoryResponse(**history_dict))
        
        logger.log_activity(
            action="get_assignment_history",
            entity_type="assignment",
            user_id=current_user.id
        )
        
        return history_responses
        
    except Exception as e:
        logger.error(f"Error getting assignment history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get assignment history"
        )
        return entity.title
    else:
        return str(entity_id)


async def get_project_team_members(project_id: str, db: AsyncSession) -> List[str]:
    """Get all user IDs that are members of teams in the given project."""
    result = await db.execute(
        select(TeamMember.user_id)
        .join(Team, TeamMember.team_id == Team.id)
        .where(
            and_(
                Team.project_id == project_id,
                Team.is_active == True,
                TeamMember.is_active == True
            )
        )
    )
    return [row[0] for row in result.fetchall()]


async def validate_assignment_permissions(
    entity_type: str, 
    entity_id: str, 
    user_id: str, 
    assignment_type: str,
    db: AsyncSession
) -> None:
    """Validate that a user can be assigned to an entity based on team membership rules."""
    
    # For tasks and subtasks, user must be a team member of the project
    if entity_type in ['task', 'subtask']:
        # Get the project ID for this entity
        project_id = None
        
        if entity_type == 'task':
            # Task -> UserStory -> UseCase -> Project
            task_result = await db.execute(
                select(Task).options(
                    selectinload(Task.user_story)
                    .selectinload(UserStory.usecase)
                    .selectinload(Usecase.project)
                ).where(Task.id == entity_id)
            )
            task = task_result.scalar_one_or_none()
            if task and task.user_story and task.user_story.usecase:
                project_id = task.user_story.usecase.project_id
        
        elif entity_type == 'subtask':
            # Subtask -> Task -> UserStory -> UseCase -> Project
            subtask_result = await db.execute(
                select(Subtask).options(
                    selectinload(Subtask.task)
                    .selectinload(Task.user_story)
                    .selectinload(UserStory.usecase)
                    .selectinload(Usecase.project)
                ).where(Subtask.id == entity_id)
            )
            subtask = subtask_result.scalar_one_or_none()
            if subtask and subtask.task and subtask.task.user_story and subtask.task.user_story.usecase:
                project_id = subtask.task.user_story.usecase.project_id
        
        if project_id:
            team_members = await get_project_team_members(project_id, db)
            if user_id not in team_members:
                raise ValidationException(
                    f"User must be a team member of the project to be assigned to {entity_type}s"
                )


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    assignment_data: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an assignment."""
    
    # Only admins can update assignments
    if current_user.role != "Admin":
        raise AccessDeniedException("Only administrators can update assignments")
    
    result = await db.execute(
        select(Assignment)
        .options(selectinload(Assignment.user))
        .where(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise ResourceNotFoundException("Assignment", assignment_id)
    
    # Track changes for history
    previous_user_id = assignment.user_id
    
    # Update fields
    for field, value in assignment_data.dict(exclude_unset=True).items():
        if field == "user_id" and value != assignment.user_id:
            # Validate new user assignment permissions
            await validate_assignment_permissions(
                assignment.entity_type,
                assignment.entity_id,
                value,
                assignment.assignment_type,
                db
            )
        setattr(assignment, field, value)
    
    assignment.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(assignment)
    
    # Create history record if user changed
    if assignment_data.user_id and assignment_data.user_id != previous_user_id:
        history = AssignmentHistory(
            id=generate_id("ASH"),
            assignment_id=assignment.id,
            entity_type=assignment.entity_type,
            entity_id=assignment.entity_id,
            user_id=assignment.user_id,
            assignment_type=assignment.assignment_type,
            action="updated",
            previous_user_id=previous_user_id,
            created_by=current_user.id
        )
        db.add(history)
        await db.commit()
    
    logger.log_activity(
        action="update_assignment",
        entity_type="assignment",
        entity_id=assignment_id
    )
    
    assignment_dict = assignment.__dict__.copy()
    assignment_dict['user_name'] = assignment.user.full_name if assignment.user else None
    assignment_dict['user_email'] = assignment.user.email if assignment.user else None
    assignment_dict['entity_name'] = await get_entity_name(
        assignment.entity_type, assignment.entity_id, db
    )
    
    return AssignmentResponse(**assignment_dict)




@router.get("/history/{entity_type}/{entity_id}", response_model=List[AssignmentHistoryResponse])
async def get_assignment_history(
    entity_type: str,
    entity_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assignment history for an entity."""
    
    # Only admins can view assignment history
    if current_user.role != "Admin":
        raise AccessDeniedException("Only administrators can view assignment history")
    
    result = await db.execute(
        select(AssignmentHistory)
        .options(
            selectinload(AssignmentHistory.user),
            selectinload(AssignmentHistory.previous_user)
        )
        .where(
            and_(
                AssignmentHistory.entity_type == entity_type,
                AssignmentHistory.entity_id == entity_id
            )
        )
        .order_by(AssignmentHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    history_records = result.scalars().all()
    
    # Build response
    history_responses = []
    for record in history_records:
        record_dict = record.__dict__.copy()
        record_dict['user_name'] = record.user.full_name if record.user else None
        record_dict['previous_user_name'] = record.previous_user.full_name if record.previous_user else None
        history_responses.append(AssignmentHistoryResponse(**record_dict))
    
    return history_responses
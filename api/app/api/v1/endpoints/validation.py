"""
Validation and utility endpoints for the Worky API.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import AvailableAssigneeResponse
from app.core.security import get_current_user
from app.core.logging import StructuredLogger
from app.services.validation_service import ValidationService
from app.services.assignment_service import AssignmentService

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/eligible-users/{entity_type}/{entity_id}", response_model=List[AvailableAssigneeResponse])
async def get_eligible_users(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    assignment_type: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users eligible for assignment to a specific entity."""
    
    validation_service = ValidationService(db)
    assignment_service = AssignmentService(db)
    
    try:
        eligible_users = await validation_service.get_eligible_users_for_entity(
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
            
            # Check if user is a team member (for project-level entities)
            is_team_member = False
            if entity_type in ["usecase", "userstory", "task", "subtask"]:
                project_id = await validation_service.get_project_from_entity(entity_type, entity_id)
                if project_id:
                    is_team_member = await validation_service.validate_team_membership(user.id, project_id)
            
            assignee_dict = {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.primary_role,
                "is_team_member": is_team_member,
                "current_assignments": current_assignments
            }
            assignee_responses.append(AvailableAssigneeResponse(**assignee_dict))
        
        logger.log_activity(
            action="get_eligible_users",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return assignee_responses
        
    except Exception as e:
        logger.log_error(f"Error getting eligible users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get eligible users"
        )


@router.post("/assignment", response_model=Dict[str, Any])
async def validate_assignment(
    validation_data: Dict[str, str],  # {"entity_type": "...", "entity_id": "...", "user_id": "...", "assignment_type": "..."}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate assignment rules before creating an assignment."""
    
    validation_service = ValidationService(db)
    
    # Validate required fields
    required_fields = ["entity_type", "entity_id", "user_id", "assignment_type"]
    missing_fields = [field for field in required_fields if field not in validation_data]
    
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    try:
        validation_result = await validation_service.validate_assignment_rules(
            entity_type=validation_data["entity_type"],
            entity_id=validation_data["entity_id"],
            user_id=validation_data["user_id"],
            assignment_type=validation_data["assignment_type"]
        )
        
        # Check for conflicts
        conflicts = await validation_service.check_assignment_conflicts(
            entity_type=validation_data["entity_type"],
            entity_id=validation_data["entity_id"],
            user_id=validation_data["user_id"]
        )
        
        result = validation_result.to_dict()
        result["conflicts"] = [{"type": c.conflict_type, "message": c.message} for c in conflicts]
        
        logger.log_activity(
            action="validate_assignment",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        logger.log_error(f"Error validating assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate assignment"
        )


@router.get("/team-members/{project_id}", response_model=List[AvailableAssigneeResponse])
async def get_project_team_members(
    project_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all members of a project's team."""
    
    try:
        # Get project team
        team_query = select(Team).options(
            selectinload(Team.members).selectinload(TeamMember.user)
        ).where(
            and_(
                Team.project_id == project_id,
                Team.is_active == True
            )
        )
        
        team_result = await db.execute(team_query)
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active team found for this project"
            )
        
        # Convert to response format
        member_responses = []
        for member in team.members:
            if member.is_active and member.user:
                member_dict = {
                    "id": member.user.id,
                    "full_name": member.user.full_name,
                    "email": member.user.email,
                    "role": member.user.primary_role,
                    "is_team_member": True,
                    "current_assignments": []  # Could be populated if needed
                }
                member_responses.append(AvailableAssigneeResponse(**member_dict))
        
        logger.log_activity(
            action="get_project_team_members",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return member_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(f"Error getting project team members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project team members"
        )


@router.get("/assignment-rules", response_model=Dict[str, Dict[str, List[str]]])
async def get_assignment_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the complete assignment rules matrix."""
    
    validation_service = ValidationService(db)
    
    try:
        rules = validation_service.get_assignment_rules_matrix()
        
        logger.log_activity(
            action="get_assignment_rules",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return rules
        
    except Exception as e:
        logger.log_error(f"Error getting assignment rules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get assignment rules"
        )


@router.post("/bulk-assignments", response_model=Dict[str, Any])
async def validate_bulk_assignments(
    assignments: List[Dict[str, str]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate a list of assignments for bulk operations."""
    
    validation_service = ValidationService(db)
    
    try:
        validation_results = await validation_service.validate_bulk_assignments(assignments)
        
        logger.log_activity(
            action="validate_bulk_assignments",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return validation_results
        
    except Exception as e:
        logger.log_error(f"Error validating bulk assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate bulk assignments"
        )


@router.get("/project-isolation/{entity_type}/{entity_id}", response_model=Dict[str, Any])
async def validate_project_isolation(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate that project isolation rules are maintained for an assignment."""
    
    validation_service = ValidationService(db)
    
    try:
        validation_result = await validation_service.validate_project_isolation(
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id
        )
        
        logger.log_activity(
            action="validate_project_isolation",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return validation_result.to_dict()
        
    except Exception as e:
        logger.log_error(f"Error validating project isolation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate project isolation"
        )


@router.get("/team-access/{team_id}", response_model=Dict[str, Any])
async def validate_team_access(
    team_id: str = Path(...),
    user_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate if a user has access to modify a team."""
    
    validation_service = ValidationService(db)
    
    # Use provided user_id or current user
    target_user_id = user_id or current_user.id
    
    # Get target user
    if target_user_id != current_user.id:
        user_query = select(User).where(User.id == target_user_id)
        user_result = await db.execute(user_query)
        target_user = user_result.scalar_one_or_none()
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    else:
        target_user = current_user
    
    try:
        # Get team to validate access for assignment operations
        team_query = select(Team).where(Team.id == team_id)
        team_result = await db.execute(team_query)
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Validate team access for assignment operations
        validation_result = await validation_service.validate_team_access_for_assignment(
            entity_type="project",  # Teams are project-level
            entity_id=team.project_id,
            current_user=target_user
        )
        
        logger.log_activity(
            action="validate_team_access",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return validation_result.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(f"Error validating team access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate team access"
        )


@router.get("/entity-exists/{entity_type}/{entity_id}", response_model=Dict[str, Any])
async def validate_entity_exists(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate that an entity exists in the database."""
    
    validation_service = ValidationService(db)
    
    try:
        exists = await validation_service.validate_entity_exists(entity_type, entity_id)
        
        result = {
            "valid": exists,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "exists": exists
        }
        
        if not exists:
            result["error"] = f"Entity {entity_type}:{entity_id} not found"
        
        logger.log_activity(
            action="validate_entity_exists",
            entity_type="validation",
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        logger.log_error(f"Error validating entity existence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate entity existence"
        )
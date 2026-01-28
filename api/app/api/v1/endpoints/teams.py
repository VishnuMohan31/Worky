"""
Team management endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.models.team import Team, TeamMember
from app.models.user import User
from app.models.hierarchy import Project
from app.schemas.team import (
    TeamCreate, TeamUpdate, TeamResponse, TeamWithMembersResponse,
    TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse
)
from app.core.security import get_current_user
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException, ValidationException
from app.core.logging import StructuredLogger
from app.core.utils import generate_id
from app.services.team_service import TeamService
from app.core.pagination import PaginationParams, PaginatedResponse, pagination_service

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=PaginatedResponse[TeamResponse])
async def list_teams(
    project_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List teams with optional filters."""
    
    # Check if user is Admin - prioritize role field over primary_role
    is_admin = current_user.role == "Admin" or current_user.primary_role == "Admin"
    
    # Build base query for teams
    base_query = select(Team)
    
    # Apply filters
    filters = []
    if project_id:
        filters.append(Team.project_id == project_id)
    if is_active is not None:
        filters.append(Team.is_active == is_active)
    
    # Non-admin users can only see teams they're members of
    if not is_admin:
        member_teams_subquery = select(TeamMember.team_id).where(
            and_(
                TeamMember.user_id == current_user.id,
                TeamMember.is_active == True
            )
        )
        filters.append(Team.id.in_(member_teams_subquery))
    
    # Apply filters to base query
    if filters:
        base_query = base_query.where(and_(*filters))
    
    # Create pagination parameters
    pagination = PaginationParams(page=page, per_page=per_page)
    
    # Count query - use the same filters as base_query
    count_query = select(func.count(Team.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    
    # Execute count query
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0
    
    # Get paginated results (no need to load members relationship for list view)
    paginated_query = base_query.offset(pagination.offset).limit(pagination.limit)
    items_result = await db.execute(paginated_query)
    items = items_result.scalars().all()
    
    # Get team IDs for member count query
    team_ids = [team.id for team in items]
    
    # Query member counts directly from database for accuracy
    # Initialize all teams with 0 count first
    member_counts = {team.id: 0 for team in items}
    
    if team_ids:
        # Count active team members (only TeamMember.is_active, not User.is_active)
        # This matches the logic in get_team_members service
        count_query = select(
            TeamMember.team_id,
            func.count(TeamMember.id).label('count')
        ).join(User, TeamMember.user_id == User.id).where(
            and_(
                TeamMember.team_id.in_(team_ids),
                TeamMember.is_active == True,
                User.is_active == True  # Also check user is active
            )
        ).group_by(TeamMember.team_id)
        
        count_result = await db.execute(count_query)
        # Access result - SQLAlchemy returns Row objects
        for row in count_result.all():
            try:
                # Try accessing as attribute (preferred)
                team_id = row.team_id
                count = row.count
            except (AttributeError, IndexError):
                # Fallback to tuple access
                team_id = row[0]
                count = row[1]
            
            member_counts[team_id] = int(count) if count is not None else 0
    
    # Convert to response format with accurate member count
    team_responses = []
    for team in items:
        team_dict = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "project_id": team.project_id,
            "is_active": team.is_active,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "created_by": team.created_by,
            "updated_by": team.updated_by,
            "member_count": member_counts.get(team.id, 0)  # Use direct DB count, default to 0
        }
        team_responses.append(TeamResponse(**team_dict))
    
    logger.log_activity(
        action="list_teams",
        entity_type="team",
        user_id=current_user.id,
        total_teams=total_count,
        page=page,
        items_count=len(team_responses)
    )
    
    logger.debug(f"List teams: found {total_count} teams, returning {len(team_responses)} items")
    
    # Return paginated response
    return PaginatedResponse.create(
        items=team_responses,
        total=total_count,
        pagination=pagination
    )


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new team."""
    
    team_service = TeamService(db)
    
    try:
        team = await team_service.create_team(
            name=team_data.name,
            description=team_data.description,
            project_id=team_data.project_id,
            current_user=current_user
        )
        
        team_dict = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "project_id": team.project_id,
            "is_active": team.is_active,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "created_by": team.created_by,
            "updated_by": team.updated_by,
            "member_count": 0
        }
        
        logger.log_activity(
            action="create_team",
            entity_type="team",
            entity_id=team.id,
            user_id=current_user.id
        )
        
        return TeamResponse(**team_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create team: {str(e)}"
        )


@router.get("/{team_id}", response_model=TeamWithMembersResponse)
async def get_team(
    team_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team details with members."""
    
    team_service = TeamService(db)
    
    # Get team
    team = await team_service.get_team_by_id(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check access
    if not await team_service.validate_team_access(team_id, current_user):
        user_role = current_user.primary_role or current_user.role
        if user_role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Get team members
    members = await team_service.get_team_members(team_id, current_user)
    
    # Convert to response format
    member_responses = []
    for member in members:
        # Get user details separately to avoid async issues
        user = await db.get(User, member.user_id)
        
        # Skip if user is not found or inactive (to match count query logic)
        if not user or not user.is_active:
            continue
        
        member_dict = {
            "id": member.id,
            "team_id": member.team_id,
            "user_id": member.user_id,
            "role": member.role,
            "joined_at": member.joined_at,
            "is_active": member.is_active,
            "user_name": user.full_name if user else None,
            "user_email": user.email if user else None
        }
        member_responses.append(TeamMemberResponse(**member_dict))
    
    team_dict = {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "project_id": team.project_id,
        "is_active": team.is_active,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
        "created_by": team.created_by,
        "updated_by": team.updated_by,
        "member_count": len(member_responses),
        "members": member_responses
    }
    
    logger.log_activity(
        action="get_team",
        entity_type="team",
        entity_id=team_id,
        user_id=current_user.id
    )
    
    return TeamWithMembersResponse(**team_dict)


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str = Path(...),
    team_data: TeamUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update team information."""
    
    team_service = TeamService(db)
    
    try:
        team = await team_service.update_team(
            team_id=team_id,
            name=team_data.name,
            description=team_data.description,
            project_id=team_data.project_id,
            current_user=current_user
        )
        
        team_dict = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "project_id": team.project_id,
            "is_active": team.is_active,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "created_by": team.created_by,
            "updated_by": team.updated_by,
            "member_count": 0  # We don't load members here for performance
        }
        
        logger.log_activity(
            action="update_team",
            entity_type="team",
            entity_id=team_id,
            user_id=current_user.id
        )
        
        return TeamResponse(**team_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update team"
        )


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    member_data: TeamMemberCreate,
    team_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a member to a team."""
    
    team_service = TeamService(db)
    
    try:
        member = await team_service.add_member(
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role,
            current_user=current_user
        )
        
        # Get user details separately to avoid async issues
        user = await db.get(User, member.user_id)
        
        member_dict = {
            "id": member.id,
            "team_id": member.team_id,
            "user_id": member.user_id,
            "role": member.role,
            "joined_at": member.joined_at,
            "is_active": member.is_active,
            "user_name": user.full_name if user else None,
            "user_email": user.email if user else None
        }
        
        return TeamMemberResponse(**member_dict)
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as-is (these are expected business logic errors)
        raise http_exc
    except Exception as e:
        # Return 500 without logging to avoid logger issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add team member: {str(e)}"
        )


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: str = Path(...),
    user_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from a team."""
    
    team_service = TeamService(db)
    
    try:
        success = await team_service.remove_member(
            team_id=team_id,
            user_id=user_id,
            current_user=current_user
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        logger.log_activity(
            action="remove_team_member",
            entity_type="team_member",
            user_id=current_user.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing team member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove team member"
        )


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: str = Path(...),
    is_active: Optional[bool] = Query(None),  # None means return all, True/False for filtering
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List team members."""
    
    team_service = TeamService(db)
    
    try:
        # Get all team members from service
        all_members = await team_service.get_team_members(team_id, current_user)
        
        logger.debug(f"list_team_members: got {len(all_members)} total members from service for team {team_id}")
        
        # Filter by active status - default to active members only for UI
        if is_active is None:
            # Default behavior: show only active members for UI
            members = [m for m in all_members if m.is_active == True]
        else:
            # Explicit filtering based on query parameter
            members = [m for m in all_members if m.is_active == is_active]
        
        logger.debug(f"list_team_members: after filtering, {len(members)} members remain for team {team_id}")
        
        # Convert to response format
        member_responses = []
        for member in members:
            # Get user details separately to avoid async issues
            user = await db.get(User, member.user_id)
            
            # Skip if user is not found or inactive (to match count query logic)
            if not user or not user.is_active:
                continue
            
            member_dict = {
                "id": member.id,
                "team_id": member.team_id,
                "user_id": member.user_id,
                "role": member.role,
                "joined_at": member.joined_at,
                "is_active": member.is_active,
                "user_name": user.full_name if user else None,
                "user_email": user.email if user else None
            }
            member_responses.append(TeamMemberResponse(**member_dict))
        
        logger.debug(f"list_team_members: returning {len(member_responses)} member responses for team {team_id}")
        
        logger.log_activity(
            action="list_team_members",
            entity_type="team",
            entity_id=team_id,
            user_id=current_user.id
        )
        
        return member_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing team members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list team members"
        )


@router.get("/project/{project_id}", response_model=TeamWithMembersResponse)
async def get_project_team(
    project_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the team assigned to a project."""
    
    team_service = TeamService(db)
    
    try:
        team = await team_service.get_project_team(project_id)
        
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No team found for this project"
            )
        
        # Convert to response format
        member_responses = []
        for member in team.members:
            if member.is_active:
                # Get user details separately to avoid async issues
                user = await db.get(User, member.user_id)
                
                # Skip if user is not found or inactive (to match count query logic)
                if not user or not user.is_active:
                    continue
                
                member_dict = {
                    "id": member.id,
                    "team_id": member.team_id,
                    "user_id": member.user_id,
                    "role": member.role,
                    "joined_at": member.joined_at,
                    "is_active": member.is_active,
                    "user_name": user.full_name if user else None,
                    "user_email": user.email if user else None
                }
                member_responses.append(TeamMemberResponse(**member_dict))
        
        team_dict = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "project_id": team.project_id,
            "is_active": team.is_active,
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "created_by": team.created_by,
            "updated_by": team.updated_by,
            "member_count": len(member_responses),
            "members": member_responses
        }
        
        logger.log_activity(
            action="get_project_team",
            entity_type="team",
            entity_id=team.id,
            user_id=current_user.id
        )
        
        return TeamWithMembersResponse(**team_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project team"
        )
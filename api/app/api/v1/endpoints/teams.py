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
    
    query = select(Team).options(selectinload(Team.members))
    
    # Apply filters
    if project_id:
        query = query.where(Team.project_id == project_id)
    if is_active is not None:
        query = query.where(Team.is_active == is_active)
    
    # Non-admin users can only see teams they're members of or have access to
    user_role = current_user.primary_role or current_user.role
    if user_role != "Admin":
        # Subquery to get team IDs where user is a member
        member_teams_subquery = select(TeamMember.team_id).where(
            and_(
                TeamMember.user_id == current_user.id,
                TeamMember.is_active == True
            )
        )
        query = query.where(Team.id.in_(member_teams_subquery))
    
    # Create pagination parameters
    pagination = PaginationParams(page=page, per_page=per_page)
    
    # Get paginated results
    items, total_count = await pagination_service.paginate_query(
        db=db,
        query=query,
        pagination=pagination
    )
    
    # Convert to response format with member count
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
            "member_count": len([m for m in team.members if m.is_active])
        }
        team_responses.append(TeamResponse(**team_dict))
    
    logger.log_activity(
        action="list_teams",
        entity_type="team",
        user_id=current_user.id,
        total_teams=total_count,
        page=page
    )
    
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
        logger.error(f"Error creating team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team"
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
    team_id: str = Path(...),
    member_data: TeamMemberCreate = None,
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
        
        logger.log_activity(
            action="add_team_member",
            entity_type="team_member",
            entity_id=member.id,
            user_id=current_user.id
        )
        
        return TeamMemberResponse(**member_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding team member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add team member"
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
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List team members."""
    
    team_service = TeamService(db)
    
    try:
        members = await team_service.get_team_members(team_id, current_user)
        
        # Filter by active status if specified
        if is_active is not None:
            members = [m for m in members if m.is_active == is_active]
        
        # Convert to response format
        member_responses = []
        for member in members:
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
            member_responses.append(TeamMemberResponse(**member_dict))
        
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
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    teams = result.scalars().all()
    
    # Add member count to each team
    team_responses = []
    for team in teams:
        team_dict = team.__dict__.copy()
        team_dict['member_count'] = len([m for m in team.members if m.is_active])
        team_responses.append(TeamResponse(**team_dict))
    
    return team_responses


@router.get("/{team_id}", response_model=TeamWithMembersResponse)
async def get_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific team with its members."""
    
    result = await db.execute(
        select(Team)
        .options(
            selectinload(Team.members).selectinload(TeamMember.user),
            selectinload(Team.project)
        )
        .where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise ResourceNotFoundException("Team", team_id)
    
    # Check access - admin or team member
    if current_user.role != "Admin":
        is_member = any(
            m.user_id == current_user.id and m.is_active 
            for m in team.members
        )
        if not is_member:
            raise AccessDeniedException("You can only view teams you're a member of")
    
    # Build response with member details
    members = []
    for member in team.members:
        if member.is_active:
            # Get user details separately to avoid async issues
            user = await db.get(User, member.user_id)
            
            member_dict = member.__dict__.copy()
            member_dict['user_name'] = user.full_name if user else None
            member_dict['user_email'] = user.email if user else None
            members.append(TeamMemberResponse(**member_dict))
    
    team_dict = team.__dict__.copy()
    team_dict['member_count'] = len(members)
    team_dict['members'] = members
    
    return TeamWithMembersResponse(**team_dict)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a team."""
    
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()
    
    if not team:
        raise ResourceNotFoundException("Team", team_id)
    
    # Only admins can delete teams
    if current_user.role != "Admin":
        raise AccessDeniedException("Only administrators can delete teams")
    
    team.is_active = False
    team.updated_by = current_user.id
    
    # Also deactivate all team members
    await db.execute(
        select(TeamMember)
        .where(TeamMember.team_id == team_id)
        .update({"is_active": False})
    )
    
    await db.commit()
    
    logger.log_activity(
        action="delete_team",
        entity_type="team",
        entity_id=team_id
    )


# Team Member Management Endpoints

@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: str,
    member_data: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a member to a team."""
    
    # Verify team exists
    team_result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = team_result.scalar_one_or_none()
    
    if not team:
        raise ResourceNotFoundException("Team", team_id)
    
    # Only admins can add team members
    if current_user.role != "Admin":
        raise AccessDeniedException("Only administrators can add team members")
    
    # Verify user exists
    user_result = await db.execute(
        select(User).where(User.id == member_data.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise ResourceNotFoundException("User", member_data.user_id)
    
    # Check if user is already a member
    existing_member = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == member_data.user_id,
                TeamMember.is_active == True
            )
        )
    )
    if existing_member.scalar_one_or_none():
        raise ValidationException("User is already a member of this team")
    
    team_member = TeamMember(
        id=generate_id("TM"),
        team_id=team_id,
        **member_data.dict(),
        created_by=current_user.id
    )
    
    db.add(team_member)
    await db.commit()
    await db.refresh(team_member)
    
    logger.log_activity(
        action="add_team_member",
        entity_type="team_member",
        entity_id=team_member.id,
        team_id=team_id,
        user_id=member_data.user_id
    )
    
    member_dict = team_member.__dict__.copy()
    member_dict['user_name'] = user.full_name
    member_dict['user_email'] = user.email
    return TeamMemberResponse(**member_dict)


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from a team."""
    
    # Only admins can remove team members
    if current_user.role != "Admin":
        raise AccessDeniedException("Only administrators can remove team members")
    
    result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        )
    )
    team_member = result.scalar_one_or_none()
    
    if not team_member:
        raise ResourceNotFoundException("Team member", f"{team_id}/{user_id}")
    
    team_member.is_active = False
    
    await db.commit()
    
    logger.log_activity(
        action="remove_team_member",
        entity_type="team_member",
        entity_id=team_member.id,
        team_id=team_id,
        user_id=user_id
    )


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    team_id: str,
    is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all members of a team."""
    
    # Verify team exists and user has access
    team_result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = team_result.scalar_one_or_none()
    
    if not team:
        raise ResourceNotFoundException("Team", team_id)
    
    # Check access - admin or team member
    if current_user.role != "Admin":
        member_check = await db.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == current_user.id,
                    TeamMember.is_active == True
                )
            )
        )
        if not member_check.scalar_one_or_none():
            raise AccessDeniedException("You can only view members of teams you belong to")
    
    query = select(TeamMember).options(selectinload(TeamMember.user)).where(
        TeamMember.team_id == team_id
    )
    
    if is_active is not None:
        query = query.where(TeamMember.is_active == is_active)
    
    result = await db.execute(query)
    members = result.scalars().all()
    
    member_responses = []
    for member in members:
        # Get user details separately to avoid async issues
        user = await db.get(User, member.user_id)
        
        member_dict = member.__dict__.copy()
        member_dict['user_name'] = user.full_name if user else None
        member_dict['user_email'] = user.email if user else None
        member_responses.append(TeamMemberResponse(**member_dict))
    
    return member_responses
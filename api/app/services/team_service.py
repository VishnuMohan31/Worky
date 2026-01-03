"""
Team Service for managing team operations and team member management.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime

from app.models.team import Team, TeamMember
from app.models.user import User
from app.models.hierarchy import Project
from app.core.utils import generate_id
from app.services.notification_service import notification_service
from app.services.cache_service import cache_service


class TeamService:
    """Service for managing team operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_team(
        self, 
        name: str,
        description: Optional[str],
        project_id: str,
        current_user: User
    ) -> Team:
        """
        Create a new team for a project.
        
        Requirements: 2.1, 2.2
        """
        # Verify project exists and user has access
        project_query = select(Project).where(Project.id == project_id)
        project_result = await self.db.execute(project_query)
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if user has permission to create teams for this project
        # For now, allow Admin, Project Manager, and Architect roles
        # Check role field first (main role), then fall back to primary_role
        # Admin users should always have role="Admin" regardless of primary_role
        user_role = current_user.role if current_user.role else current_user.primary_role
        allowed_roles = ["Admin", "Project Manager", "Architect", "Owner"]
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions to create teams. User role: {user_role}, Required: {allowed_roles}"
            )
        
        # Check if team with same name already exists for this project
        existing_team_query = select(Team).where(
            and_(
                Team.project_id == project_id,
                Team.name == name,
                Team.is_active == True
            )
        )
        existing_team_result = await self.db.execute(existing_team_query)
        existing_team = existing_team_result.scalar_one_or_none()
        
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An active team with the name '{name}' already exists for this project"
            )
        
        # Create new team
        team = Team(
            id=generate_id("TEAM"),
            name=name,
            description=description,
            project_id=project_id,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        
        return team
    
    async def add_member(
        self, 
        team_id: str, 
        user_id: str, 
        role: str, 
        current_user: User
    ) -> TeamMember:
        """
        Add a member to a team.
        
        Requirements: 2.3, 6.1
        """
        # Verify team exists
        team = await self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Verify user exists
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive"
            )
        
        # Check if user has permission to add members
        if not await self.validate_team_access(team_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify team"
            )
        
        # Check if user is already a member (active or inactive)
        existing_member_query = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id
            )
        )
        existing_member_result = await self.db.execute(existing_member_query)
        existing_member = existing_member_result.scalar_one_or_none()
        
        if existing_member:
            if existing_member.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this team"
                )
            else:
                # Reactivate the inactive member instead of creating a new one
                existing_member.is_active = True
                existing_member.role = role
                await self.db.commit()
                await self.db.refresh(existing_member)
                
                # Load the user relationship explicitly
                await self.db.refresh(existing_member, ["user"])
                
                logger.info(f"Team member {user_id} reactivated in team {team_id} with role {role}")
                return existing_member
        
        # Validate role
        valid_roles = ["Owner", "Developer", "Tester", "Architect", "Designer", "Contact Person", "Member", "Lead", "Manager"]
        if role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Create team member
        team_member = TeamMember(
            id=generate_id("TM"),
            team_id=team_id,
            user_id=user_id,
            role=role,
            created_by=current_user.id
        )
        
        self.db.add(team_member)
        await self.db.commit()
        await self.db.refresh(team_member)
        
        # Load the user relationship explicitly to avoid async issues
        await self.db.refresh(team_member, ["user"])
        
        # Invalidate caches
        cache_service.invalidate_team_members(team_id)
        cache_service.invalidate_user_teams(user_id)
        cache_service.invalidate_project_team(team.project_id)
        
        # Send team member added notification (temporarily disabled to avoid async issues)
        # TODO: Re-enable notifications after fixing async context issues
        try:
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.info(f"Team member {user_id} added to team {team_id} with role {role}")
            # Notification temporarily disabled
            # project_result = await self.db.execute(select(Project).where(Project.id == team.project_id))
            # project = project_result.scalar_one_or_none()
            # 
            # await notification_service.notify_team_member_added(
            #     self.db,
            #     added_user_id=user_id,
            #     team_id=team_id,
            #     team_name=team.name,
            #     project_id=team.project_id,
            #     project_name=project.name if project else None,
            #     added_by_id=current_user.id,
            #     role=role
            # )
        except Exception as e:
            # Log error but don't fail the team member addition
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.error(f"Failed to send team member added notification: {str(e)}")
        
        return team_member
    
    async def remove_member(
        self, 
        team_id: str, 
        user_id: str, 
        current_user: User
    ) -> bool:
        """
        Remove a member from a team.
        
        Requirements: 2.3, 4.4
        """
        # Verify team exists
        team = await self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Check if user has permission to remove members
        if not await self.validate_team_access(team_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify team"
            )
        
        # Find team member
        member_query = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        )
        member_result = await self.db.execute(member_query)
        member = member_result.scalar_one_or_none()
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Send team member removed notification before removing (temporarily disabled)
        # TODO: Re-enable notifications after fixing async context issues
        try:
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.info(f"Team member {user_id} removed from team {team_id}")
            # Notification temporarily disabled
            # project_result = await self.db.execute(select(Project).where(Project.id == team.project_id))
            # project = project_result.scalar_one_or_none()
            # 
            # await notification_service.notify_team_member_removed(
            #     self.db,
            #     removed_user_id=user_id,
            #     team_id=team_id,
            #     team_name=team.name,
            #     project_id=team.project_id,
            #     project_name=project.name if project else None,
            #     removed_by_id=current_user.id
            # )
        except Exception as e:
            # Log error but don't fail the team member removal
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.error(f"Failed to send team member removed notification: {str(e)}")
        
        # Soft delete (deactivate) the member
        member.is_active = False
        await self.db.commit()
        
        # Invalidate caches
        cache_service.invalidate_team_members(team_id)
        cache_service.invalidate_user_teams(user_id)
        cache_service.invalidate_project_team(team.project_id)
        
        return True
    
    async def get_team_members(
        self, 
        team_id: str, 
        current_user: User
    ) -> List[TeamMember]:
        """
        Get all members of a team with caching.
        
        Requirements: 2.5, 8.3, 12.1
        """
        # Check cache first
        cached_members = cache_service.get_team_members(team_id)
        if cached_members is not None:
            # Still need to verify access, but return cached data
            if await self.validate_team_access(team_id, current_user):
                return cached_members
        
        # Verify team exists and user has access
        team = await self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # For now, allow any authenticated user to view team members
        # In production, you might want to restrict this based on project access
        
        # Get team members with user information
        members_query = select(TeamMember).options(
            selectinload(TeamMember.user)
        ).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.is_active == True
            )
        )
        
        members_result = await self.db.execute(members_query)
        members = members_result.scalars().all()
        
        # Cache the results
        members_list = list(members)
        cache_service.set_team_members(team_id, members_list)
        
        return members_list
    
    async def validate_team_access(
        self, 
        team_id: str, 
        current_user: User
    ) -> bool:
        """
        Validate if user has access to modify a team.
        
        Requirements: 4.1, 4.2
        """
        # Admin users have access to all teams - check role first, then primary_role
        is_admin = current_user.role == "Admin" or current_user.primary_role == "Admin"
        if is_admin:
            return True
        
        # Get team and check project access
        team = await self.get_team_by_id(team_id)
        if not team:
            return False
        
        # Check if user is a member of the team or has appropriate role
        user_role = current_user.role if current_user.role else current_user.primary_role
        if user_role in ["Project Manager", "Architect", "Owner"]:
            return True
        
        # Check if user is a team member with appropriate permissions
        member_query = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
                TeamMember.is_active == True,
                TeamMember.role.in_(["Owner", "Project Manager"])
            )
        )
        member_result = await self.db.execute(member_query)
        member = member_result.scalar_one_or_none()
        
        return member is not None
    
    async def get_project_team(
        self, 
        project_id: str
    ) -> Optional[Team]:
        """
        Get the team assigned to a project.
        
        Requirements: 2.1, 11.3
        """
        team_query = select(Team).options(
            selectinload(Team.members).selectinload(TeamMember.user)
        ).where(
            and_(
                Team.project_id == project_id,
                Team.is_active == True
            )
        )
        
        team_result = await self.db.execute(team_query)
        team = team_result.scalar_one_or_none()
        
        return team
    
    async def get_team_by_id(
        self, 
        team_id: str
    ) -> Optional[Team]:
        """
        Get a team by its ID.
        """
        team_query = select(Team).where(Team.id == team_id)
        team_result = await self.db.execute(team_query)
        team = team_result.scalar_one_or_none()
        
        return team
    
    async def update_team(
        self,
        team_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        current_user: User = None
    ) -> Team:
        """
        Update team information.
        
        Requirements: 2.2
        """
        from sqlalchemy import update as sql_update
        
        # Verify team exists
        team = await self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Check permissions
        if not await self.validate_team_access(team_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify team"
            )
        
        # Build update values dictionary
        update_values = {
            "updated_by": current_user.id,
            "updated_at": datetime.utcnow()
        }
        
        if name is not None:
            update_values["name"] = name
        if description is not None:
            update_values["description"] = description
        if project_id is not None:
            # Empty string means clear the project_id (unassign from project)
            update_values["project_id"] = project_id if project_id != "" else None
        
        # Use direct SQL update for reliability
        stmt = sql_update(Team).where(Team.id == team_id).values(**update_values)
        await self.db.execute(stmt)
        await self.db.commit()
        
        # Refresh the team object
        await self.db.refresh(team)
        
        return team
    
    async def get_user_teams(
        self,
        user_id: str
    ) -> List[Team]:
        """
        Get all teams a user is a member of.
        
        Requirements: 6.3
        """
        teams_query = select(Team).join(TeamMember).where(
            and_(
                TeamMember.user_id == user_id,
                TeamMember.is_active == True,
                Team.is_active == True
            )
        )
        
        teams_result = await self.db.execute(teams_query)
        teams = teams_result.scalars().all()
        
        return list(teams)
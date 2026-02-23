"""
Access Control Service for hierarchical entity access management.

This service implements the access control rules:
- Clients & Programs: All authenticated users can see
- Projects: Only team members assigned to the project can see (Admin excepted)
- Use Cases, User Stories, Tasks, Subtasks: ONLY users with direct assignments can see (Admin excepted)
  Team membership does NOT grant access to these entities - explicit assignment is required
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status

from app.models.user import User
from app.models.team import Team, TeamMember, Assignment
from app.models.hierarchy import Project, Usecase, UserStory, Task, Subtask


class AccessControlService:
    """Service for managing access control across the hierarchy"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _is_admin(self, user: User) -> bool:
        """Check if user is an admin"""
        return user.role == "Admin" or user.primary_role == "Admin"
    
    async def can_access_project(self, project_id: str, user: User) -> bool:
        """
        Check if user can access a project.
        
        Rules:
        - Admin: Always has access
        - Team Members: Users who are members of teams assigned to the project
        """
        # Admin has access to everything
        if self._is_admin(user):
            return True
        
        # Check if user is a member of a team assigned to this project
        query = select(TeamMember).join(Team).where(
            and_(
                Team.project_id == project_id,
                Team.is_active == True,
                TeamMember.user_id == user.id,
                TeamMember.is_active == True
            )
        )
        result = await self.db.execute(query)
        team_member = result.scalar_one_or_none()
        
        return team_member is not None
    
    async def can_access_usecase(self, usecase_id: str, user: User) -> bool:
        """
        Check if user can access a use case.
        
        Rules:
        - Admin: Always has access
        - Regular Users: ONLY if they have a direct assignment to this use case
        """
        # Admin has access to everything
        if self._is_admin(user):
            return True
        
        # Check if user has direct assignment to this use case
        # Team membership does NOT grant access to use cases
        assignment_query = select(Assignment).where(
            and_(
                Assignment.entity_type == "usecase",
                Assignment.entity_id == usecase_id,
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()
        
        return assignment is not None
    
    async def can_access_user_story(self, user_story_id: str, user: User) -> bool:
        """
        Check if user can access a user story.
        
        Rules:
        - Admin: Always has access
        - Regular Users: ONLY if they have a direct assignment to this user story
        """
        # Admin has access to everything
        if self._is_admin(user):
            return True
        
        # Check if user has direct assignment to this user story
        # Team membership does NOT grant access to user stories
        assignment_query = select(Assignment).where(
            and_(
                Assignment.entity_type == "userstory",
                Assignment.entity_id == user_story_id,
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()
        
        return assignment is not None
    
    async def can_access_task(self, task_id: str, user: User) -> bool:
        """
        Check if user can access a task.
        
        Rules:
        - Admin: Always has access
        - Regular Users: ONLY if they have a direct assignment to this task
        """
        # Admin has access to everything
        if self._is_admin(user):
            return True
        
        # Check if user has direct assignment to this task
        # Team membership does NOT grant access to tasks
        assignment_query = select(Assignment).where(
            and_(
                Assignment.entity_type == "task",
                Assignment.entity_id == task_id,
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()
        
        return assignment is not None
    
    async def can_access_subtask(self, subtask_id: str, user: User) -> bool:
        """
        Check if user can access a subtask.
        
        Rules:
        - Admin: Always has access
        - Regular Users: ONLY if they have a direct assignment to this subtask
        """
        # Admin has access to everything
        if self._is_admin(user):
            return True
        
        # Check if user has direct assignment to this subtask
        # Team membership does NOT grant access to subtasks
        assignment_query = select(Assignment).where(
            and_(
                Assignment.entity_type == "subtask",
                Assignment.entity_id == subtask_id,
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()
        
        return assignment is not None
    
    async def filter_projects_by_access(self, user: User, base_query):
        """
        Filter projects query to only include projects the user can access.
        
        Returns modified query with access control applied.
        """
        # Admin can see all projects
        if self._is_admin(user):
            return base_query
        
        # Get project IDs where user is a team member
        team_projects_subquery = select(Team.project_id).join(TeamMember).where(
            and_(
                TeamMember.user_id == user.id,
                TeamMember.is_active == True,
                Team.is_active == True,
                Team.project_id.isnot(None)
            )
        ).distinct()
        
        # Filter to only projects where user is a team member
        return base_query.where(Project.id.in_(team_projects_subquery))
    
    async def filter_usecases_by_access(self, user: User, base_query):
        """
        Filter use cases query to only include use cases the user can access.
        
        Returns modified query with access control applied.
        
        Rules:
        - Admin: Can see all use cases
        - Regular Users: Can ONLY see use cases they are directly assigned to
        """
        # Admin can see all use cases
        if self._is_admin(user):
            return base_query
        
        # Get use case IDs where user has assignments
        # ONLY assigned use cases are visible (team membership does NOT grant access)
        assigned_usecases_subquery = select(Assignment.entity_id).where(
            and_(
                Assignment.entity_type == "usecase",
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        
        # Filter to ONLY use cases where user has direct assignment
        return base_query.where(Usecase.id.in_(assigned_usecases_subquery))
    
    async def filter_user_stories_by_access(self, user: User, base_query):
        """
        Filter user stories query to only include user stories the user can access.
        
        Returns modified query with access control applied.
        
        Rules:
        - Admin: Can see all user stories
        - Regular Users: Can ONLY see user stories they are directly assigned to
        """
        # Admin can see all user stories
        if self._is_admin(user):
            return base_query
        
        # Get user story IDs where user has assignments
        # ONLY assigned user stories are visible (team membership does NOT grant access)
        assigned_stories_subquery = select(Assignment.entity_id).where(
            and_(
                Assignment.entity_type == "userstory",
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        
        # Filter to ONLY user stories where user has direct assignment
        return base_query.where(UserStory.id.in_(assigned_stories_subquery))
    
    async def filter_tasks_by_access(self, user: User, base_query):
        """
        Filter tasks query to only include tasks the user can access.
        
        Returns modified query with access control applied.
        
        Rules:
        - Admin: Can see all tasks
        - Regular Users: Can ONLY see tasks they are directly assigned to
        """
        # Admin can see all tasks
        if self._is_admin(user):
            return base_query
        
        # Get task IDs where user has assignments
        # ONLY assigned tasks are visible (team membership does NOT grant access)
        assigned_tasks_subquery = select(Assignment.entity_id).where(
            and_(
                Assignment.entity_type == "task",
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        
        # Filter to ONLY tasks where user has direct assignment
        return base_query.where(Task.id.in_(assigned_tasks_subquery))
    
    async def filter_subtasks_by_access(self, user: User, base_query):
        """
        Filter subtasks query to only include subtasks the user can access.
        
        Returns modified query with access control applied.
        
        Rules:
        - Admin: Can see all subtasks
        - Regular Users: Can ONLY see subtasks they are directly assigned to
        """
        # Admin can see all subtasks
        if self._is_admin(user):
            return base_query
        
        # Get subtask IDs where user has assignments
        # ONLY assigned subtasks are visible (team membership does NOT grant access)
        assigned_subtasks_subquery = select(Assignment.entity_id).where(
            and_(
                Assignment.entity_type == "subtask",
                Assignment.user_id == user.id,
                Assignment.is_active == True
            )
        )
        
        # Filter to ONLY subtasks where user has direct assignment
        return base_query.where(Subtask.id.in_(assigned_subtasks_subquery))

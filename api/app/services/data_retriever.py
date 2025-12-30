"""
Data Retrieval Service with RBAC for Chat Assistant

This service retrieves data from the database with strict RBAC enforcement:
- Client-level filtering (user.client_id enforcement)
- Project-level access verification
- Soft-delete filtering (is_deleted=False)
- Query methods for tasks, projects, bugs, user stories by various filters
- Aggregate queries for statistics and reports
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import selectinload, joinedload

from app.models.hierarchy import (
    Program, Project, Usecase, UserStory, Task, Subtask, Phase
)
from app.models.bug import Bug
from app.models.user import User
from app.models.client import Client
from app.schemas.chat import EntityType, ExtractedEntity

logger = logging.getLogger(__name__)


class DataRetriever:
    """Service for retrieving data with RBAC enforcement"""
    
    def __init__(self):
        """Initialize the data retriever"""
        pass
    
    # ========================================================================
    # RBAC Enforcement Methods
    # ========================================================================
    
    async def verify_client_access(
        self,
        db: AsyncSession,
        user: User,
        entity_client_id: str
    ) -> bool:
        """
        Verify user has access to entity based on client_id
        
        Args:
            db: Database session
            user: Current user
            entity_client_id: Client ID of the entity being accessed
            
        Returns:
            True if user has access, False otherwise
        """
        # Users can only access entities from their own client
        return user.client_id == entity_client_id
    
    async def verify_project_access(
        self,
        db: AsyncSession,
        user: User,
        project_id: str
    ) -> bool:
        """
        Verify user has access to a specific project
        
        Args:
            db: Database session
            user: Current user
            project_id: Project ID to verify access
            
        Returns:
            True if user has access, False otherwise
        """
        # Get project with program relationship
        result = await db.execute(
            select(Project)
            .options(joinedload(Project.program))
            .where(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return False
        
        # Verify client access through program
        return await self.verify_client_access(db, user, project.program.client_id)
    
    async def get_user_accessible_projects(
        self,
        db: AsyncSession,
        user: User
    ) -> List[str]:
        """
        Get list of project IDs accessible to user
        
        Args:
            db: Database session
            user: Current user
            
        Returns:
            List of project IDs
        """
        # Get all programs for user's client
        result = await db.execute(
            select(Program.id)
            .where(
                Program.client_id == user.client_id,
                Program.is_deleted == False
            )
        )
        program_ids = [row[0] for row in result.all()]
        
        if not program_ids:
            return []
        
        # Get all projects for these programs
        result = await db.execute(
            select(Project.id)
            .where(
                Project.program_id.in_(program_ids),
                Project.is_deleted == False
            )
        )
        project_ids = [row[0] for row in result.all()]
        
        return project_ids
    
    # ========================================================================
    # Entity Retrieval Methods
    # ========================================================================
    
    async def get_project_by_id(
        self,
        db: AsyncSession,
        user: User,
        project_id: str
    ) -> Optional[Project]:
        """
        Get project by ID with RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            project_id: Project ID
            
        Returns:
            Project if found and accessible, None otherwise
        """
        result = await db.execute(
            select(Project)
            .options(joinedload(Project.program))
            .where(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
        
        # Verify client access
        if not await self.verify_client_access(db, user, project.program.client_id):
            logger.warning(
                f"User {user.id} attempted to access project {project_id} "
                f"from different client"
            )
            return None
        
        return project
    
    async def get_projects_by_filters(
        self,
        db: AsyncSession,
        user: User,
        status: Optional[str] = None,
        program_id: Optional[str] = None,
        name_search: Optional[str] = None,
        limit: int = 20
    ) -> List[Project]:
        """
        Get projects with filters and RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            status: Filter by status
            program_id: Filter by program
            name_search: Search by name (case-insensitive)
            limit: Maximum number of results
            
        Returns:
            List of accessible projects
        """
        # Build query with client filtering
        query = (
            select(Project)
            .join(Program)
            .options(joinedload(Project.program))
            .where(
                Program.client_id == user.client_id,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        )
        
        # Apply filters
        if status:
            query = query.where(Project.status == status)
        
        if program_id:
            query = query.where(Project.program_id == program_id)
        
        if name_search:
            query = query.where(
                Project.name.ilike(f"%{name_search}%")
            )
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().unique().all()
    
    async def get_task_by_id(
        self,
        db: AsyncSession,
        user: User,
        task_id: str
    ) -> Optional[Task]:
        """
        Get task by ID with RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            task_id: Task ID
            
        Returns:
            Task if found and accessible, None otherwise
        """
        result = await db.execute(
            select(Task)
            .options(
                joinedload(Task.user_story)
                .joinedload(UserStory.usecase)
                .joinedload(Usecase.project)
                .joinedload(Project.program)
            )
            .where(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return None
        
        # Verify client access through hierarchy
        client_id = task.user_story.usecase.project.program.client_id
        if not await self.verify_client_access(db, user, client_id):
            logger.warning(
                f"User {user.id} attempted to access task {task_id} "
                f"from different client"
            )
            return None
        
        return task
    
    async def get_tasks_by_filters(
        self,
        db: AsyncSession,
        user: User,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        phase_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 20
    ) -> List[Task]:
        """
        Get tasks with filters and RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            project_id: Filter by project
            status: Filter by status
            priority: Filter by priority
            assigned_to: Filter by assignee user ID
            phase_id: Filter by phase
            start_date: Filter by due date >= start_date
            end_date: Filter by due date <= end_date
            limit: Maximum number of results
            
        Returns:
            List of accessible tasks
        """
        # Build query with client filtering through hierarchy
        query = (
            select(Task)
            .join(UserStory)
            .join(Usecase)
            .join(Project)
            .join(Program)
            .options(
                joinedload(Task.user_story),
                joinedload(Task.phase),
                joinedload(Task.assignee)
            )
            .where(
                Program.client_id == user.client_id,
                Task.is_deleted == False,
                UserStory.is_deleted == False,
                Usecase.is_deleted == False,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        )
        
        # Apply filters
        if project_id:
            query = query.where(Project.id == project_id)
        
        if status:
            query = query.where(Task.status == status)
        
        if priority:
            query = query.where(Task.priority == priority)
        
        if assigned_to:
            query = query.where(Task.assigned_to == assigned_to)
        
        if phase_id:
            query = query.where(Task.phase_id == phase_id)
        
        if start_date:
            query = query.where(Task.due_date >= start_date)
        
        if end_date:
            query = query.where(Task.due_date <= end_date)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().unique().all()
    
    async def get_bug_by_id(
        self,
        db: AsyncSession,
        user: User,
        bug_id: str
    ) -> Optional[Bug]:
        """
        Get bug by ID with RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            bug_id: Bug ID
            
        Returns:
            Bug if found and accessible, None otherwise
        """
        result = await db.execute(
            select(Bug)
            .options(
                joinedload(Bug.client),
                joinedload(Bug.project),
                joinedload(Bug.reporter),
                joinedload(Bug.assignee)
            )
            .where(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            return None
        
        # Verify client access
        if bug.client_id and not await self.verify_client_access(db, user, bug.client_id):
            logger.warning(
                f"User {user.id} attempted to access bug {bug_id} "
                f"from different client"
            )
            return None
        
        return bug
    
    async def get_bugs_by_filters(
        self,
        db: AsyncSession,
        user: User,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        reporter_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Bug]:
        """
        Get bugs with filters and RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            project_id: Filter by project
            status: Filter by status
            severity: Filter by severity
            priority: Filter by priority
            assigned_to: Filter by assignee user ID
            reporter_id: Filter by reporter user ID
            limit: Maximum number of results
            
        Returns:
            List of accessible bugs
        """
        # Build query with client filtering
        query = (
            select(Bug)
            .options(
                joinedload(Bug.project),
                joinedload(Bug.reporter),
                joinedload(Bug.assignee)
            )
            .where(
                Bug.client_id == user.client_id,
                Bug.is_deleted == False
            )
        )
        
        # Apply filters
        if project_id:
            query = query.where(Bug.project_id == project_id)
        
        if status:
            query = query.where(Bug.status == status)
        
        if severity:
            query = query.where(Bug.severity == severity)
        
        if priority:
            query = query.where(Bug.priority == priority)
        
        if assigned_to:
            query = query.where(Bug.assignee_id == assigned_to)
        
        if reporter_id:
            query = query.where(Bug.reporter_id == reporter_id)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().unique().all()
    
    async def get_user_story_by_id(
        self,
        db: AsyncSession,
        user: User,
        story_id: str
    ) -> Optional[UserStory]:
        """
        Get user story by ID with RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            story_id: User story ID
            
        Returns:
            UserStory if found and accessible, None otherwise
        """
        result = await db.execute(
            select(UserStory)
            .options(
                joinedload(UserStory.usecase)
                .joinedload(Usecase.project)
                .joinedload(Project.program)
            )
            .where(
                UserStory.id == story_id,
                UserStory.is_deleted == False
            )
        )
        story = result.scalar_one_or_none()
        
        if not story:
            return None
        
        # Verify client access through hierarchy
        client_id = story.usecase.project.program.client_id
        if not await self.verify_client_access(db, user, client_id):
            logger.warning(
                f"User {user.id} attempted to access user story {story_id} "
                f"from different client"
            )
            return None
        
        return story
    
    async def get_user_stories_by_filters(
        self,
        db: AsyncSession,
        user: User,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 20
    ) -> List[UserStory]:
        """
        Get user stories with filters and RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            project_id: Filter by project
            usecase_id: Filter by usecase
            status: Filter by status
            priority: Filter by priority
            limit: Maximum number of results
            
        Returns:
            List of accessible user stories
        """
        # Build query with client filtering through hierarchy
        query = (
            select(UserStory)
            .join(Usecase)
            .join(Project)
            .join(Program)
            .options(
                joinedload(UserStory.usecase)
            )
            .where(
                Program.client_id == user.client_id,
                UserStory.is_deleted == False,
                Usecase.is_deleted == False,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        )
        
        # Apply filters
        if project_id:
            query = query.where(Project.id == project_id)
        
        if usecase_id:
            query = query.where(UserStory.usecase_id == usecase_id)
        
        if status:
            query = query.where(UserStory.status == status)
        
        if priority:
            query = query.where(UserStory.priority == priority)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().unique().all()
    
    # ========================================================================
    # Entity Resolution from Extracted Entities
    # ========================================================================
    
    async def resolve_entities(
        self,
        db: AsyncSession,
        user: User,
        entities: List[ExtractedEntity]
    ) -> Dict[str, Any]:
        """
        Resolve extracted entities to actual database objects
        
        Args:
            db: Database session
            user: Current user
            entities: List of extracted entities from query
            
        Returns:
            Dictionary mapping entity types to resolved objects
        """
        resolved = {}
        
        for entity in entities:
            if entity.entity_id:
                # Resolve by ID
                if entity.entity_type == EntityType.PROJECT:
                    obj = await self.get_project_by_id(db, user, entity.entity_id)
                    if obj:
                        resolved.setdefault('projects', []).append(obj)
                
                elif entity.entity_type == EntityType.TASK:
                    obj = await self.get_task_by_id(db, user, entity.entity_id)
                    if obj:
                        resolved.setdefault('tasks', []).append(obj)
                
                elif entity.entity_type == EntityType.BUG:
                    obj = await self.get_bug_by_id(db, user, entity.entity_id)
                    if obj:
                        resolved.setdefault('bugs', []).append(obj)
                
                elif entity.entity_type == EntityType.USER_STORY:
                    obj = await self.get_user_story_by_id(db, user, entity.entity_id)
                    if obj:
                        resolved.setdefault('user_stories', []).append(obj)
            
            elif entity.entity_name:
                # Resolve by name (search)
                if entity.entity_type == EntityType.PROJECT:
                    objs = await self.get_projects_by_filters(
                        db, user, name_search=entity.entity_name, limit=5
                    )
                    if objs:
                        resolved.setdefault('projects', []).extend(objs)
        
        return resolved
    
    # ========================================================================
    # Aggregate Queries for Reports
    # ========================================================================
    
    async def get_task_statistics(
        self,
        db: AsyncSession,
        user: User,
        project_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get task statistics with RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            project_id: Filter by project
            start_date: Filter by created_at >= start_date
            end_date: Filter by created_at <= end_date
            
        Returns:
            Dictionary with task statistics
        """
        # Build base query with client filtering
        base_query = (
            select(Task)
            .join(UserStory)
            .join(Usecase)
            .join(Project)
            .join(Program)
            .where(
                Program.client_id == user.client_id,
                Task.is_deleted == False,
                UserStory.is_deleted == False,
                Usecase.is_deleted == False,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        )
        
        # Apply filters
        if project_id:
            base_query = base_query.where(Project.id == project_id)
        
        if start_date:
            base_query = base_query.where(Task.created_at >= start_date)
        
        if end_date:
            base_query = base_query.where(Task.created_at <= end_date)
        
        # Count by status
        status_query = (
            select(
                Task.status,
                func.count(Task.id).label('count')
            )
            .select_from(base_query.subquery())
            .group_by(Task.status)
        )
        
        result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in result.all()}
        
        # Count by priority
        priority_query = (
            select(
                Task.priority,
                func.count(Task.id).label('count')
            )
            .select_from(base_query.subquery())
            .group_by(Task.priority)
        )
        
        result = await db.execute(priority_query)
        priority_counts = {row[0]: row[1] for row in result.all()}
        
        # Total count
        total_query = select(func.count()).select_from(base_query.subquery())
        result = await db.execute(total_query)
        total_count = result.scalar()
        
        return {
            'total_tasks': total_count,
            'by_status': status_counts,
            'by_priority': priority_counts
        }
    
    async def get_bug_statistics(
        self,
        db: AsyncSession,
        user: User,
        project_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get bug statistics with RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            project_id: Filter by project
            start_date: Filter by created_at >= start_date
            end_date: Filter by created_at <= end_date
            
        Returns:
            Dictionary with bug statistics
        """
        # Build base query with client filtering
        query = (
            select(Bug)
            .where(
                Bug.client_id == user.client_id,
                Bug.is_deleted == False
            )
        )
        
        # Apply filters
        if project_id:
            query = query.where(Bug.project_id == project_id)
        
        if start_date:
            query = query.where(Bug.created_at >= start_date)
        
        if end_date:
            query = query.where(Bug.created_at <= end_date)
        
        # Count by status
        status_query = (
            select(
                Bug.status,
                func.count(Bug.id).label('count')
            )
            .where(
                Bug.client_id == user.client_id,
                Bug.is_deleted == False
            )
            .group_by(Bug.status)
        )
        
        if project_id:
            status_query = status_query.where(Bug.project_id == project_id)
        if start_date:
            status_query = status_query.where(Bug.created_at >= start_date)
        if end_date:
            status_query = status_query.where(Bug.created_at <= end_date)
        
        result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in result.all()}
        
        # Count by severity
        severity_query = (
            select(
                Bug.severity,
                func.count(Bug.id).label('count')
            )
            .where(
                Bug.client_id == user.client_id,
                Bug.is_deleted == False
            )
            .group_by(Bug.severity)
        )
        
        if project_id:
            severity_query = severity_query.where(Bug.project_id == project_id)
        if start_date:
            severity_query = severity_query.where(Bug.created_at >= start_date)
        if end_date:
            severity_query = severity_query.where(Bug.created_at <= end_date)
        
        result = await db.execute(severity_query)
        severity_counts = {row[0]: row[1] for row in result.all()}
        
        # Count by priority
        priority_query = (
            select(
                Bug.priority,
                func.count(Bug.id).label('count')
            )
            .where(
                Bug.client_id == user.client_id,
                Bug.is_deleted == False
            )
            .group_by(Bug.priority)
        )
        
        if project_id:
            priority_query = priority_query.where(Bug.project_id == project_id)
        if start_date:
            priority_query = priority_query.where(Bug.created_at >= start_date)
        if end_date:
            priority_query = priority_query.where(Bug.created_at <= end_date)
        
        result = await db.execute(priority_query)
        priority_counts = {row[0]: row[1] for row in result.all()}
        
        # Total count
        total_query = (
            select(func.count(Bug.id))
            .where(
                Bug.client_id == user.client_id,
                Bug.is_deleted == False
            )
        )
        
        if project_id:
            total_query = total_query.where(Bug.project_id == project_id)
        if start_date:
            total_query = total_query.where(Bug.created_at >= start_date)
        if end_date:
            total_query = total_query.where(Bug.created_at <= end_date)
        
        result = await db.execute(total_query)
        total_count = result.scalar()
        
        return {
            'total_bugs': total_count,
            'by_status': status_counts,
            'by_severity': severity_counts,
            'by_priority': priority_counts
        }
    
    async def get_project_statistics(
        self,
        db: AsyncSession,
        user: User
    ) -> Dict[str, Any]:
        """
        Get project statistics with RBAC enforcement
        
        Args:
            db: Database session
            user: Current user
            
        Returns:
            Dictionary with project statistics
        """
        # Count by status
        status_query = (
            select(
                Project.status,
                func.count(Project.id).label('count')
            )
            .join(Program)
            .where(
                Program.client_id == user.client_id,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
            .group_by(Project.status)
        )
        
        result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in result.all()}
        
        # Total count
        total_query = (
            select(func.count(Project.id))
            .join(Program)
            .where(
                Program.client_id == user.client_id,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        )
        
        result = await db.execute(total_query)
        total_count = result.scalar()
        
        return {
            'total_projects': total_count,
            'by_status': status_counts
        }
    
    async def get_user_workload(
        self,
        db: AsyncSession,
        user: User,
        target_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get workload statistics for a user
        
        Args:
            db: Database session
            user: Current user (for RBAC)
            target_user_id: User ID to get workload for (defaults to current user)
            
        Returns:
            Dictionary with workload statistics
        """
        if not target_user_id:
            target_user_id = user.id
        
        # Verify target user is in same client
        result = await db.execute(
            select(User).where(User.id == target_user_id)
        )
        target_user = result.scalar_one_or_none()
        
        if not target_user or target_user.client_id != user.client_id:
            logger.warning(
                f"User {user.id} attempted to access workload for user {target_user_id} "
                f"from different client"
            )
            return {}
        
        # Count assigned tasks by status
        task_query = (
            select(
                Task.status,
                func.count(Task.id).label('count')
            )
            .join(UserStory)
            .join(Usecase)
            .join(Project)
            .join(Program)
            .where(
                Task.assigned_to == target_user_id,
                Program.client_id == user.client_id,
                Task.is_deleted == False,
                UserStory.is_deleted == False,
                Usecase.is_deleted == False,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
            .group_by(Task.status)
        )
        
        result = await db.execute(task_query)
        task_counts = {row[0]: row[1] for row in result.all()}
        
        # Count assigned bugs by status
        bug_query = (
            select(
                Bug.status,
                func.count(Bug.id).label('count')
            )
            .where(
                Bug.assignee_id == target_user_id,
                Bug.client_id == user.client_id,
                Bug.is_deleted == False
            )
            .group_by(Bug.status)
        )
        
        result = await db.execute(bug_query)
        bug_counts = {row[0]: row[1] for row in result.all()}
        
        return {
            'user_id': target_user_id,
            'user_name': target_user.full_name,
            'tasks_by_status': task_counts,
            'bugs_by_status': bug_counts,
            'total_tasks': sum(task_counts.values()),
            'total_bugs': sum(bug_counts.values())
        }


# Singleton instance
_data_retriever: Optional[DataRetriever] = None


def get_data_retriever() -> DataRetriever:
    """Get or create the data retriever singleton"""
    global _data_retriever
    if _data_retriever is None:
        _data_retriever = DataRetriever()
    return _data_retriever

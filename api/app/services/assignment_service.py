"""
Assignment Service for managing entity assignments and assignment operations.
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime

from app.models.team import Assignment, AssignmentHistory, Team, TeamMember
from app.models.user import User
from app.models.hierarchy import Project, Program, Usecase, UserStory, Task, Subtask
from app.models.client import Client
from app.core.utils import generate_id
from app.services.notification_service import notification_service
from app.services.cache_service import cache_service


class AssignmentService:
    """Service for managing entity assignments"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def assign_entity(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        assignment_type: str,
        current_user: User
    ) -> Assignment:
        """
        Assign an entity to a user - simplified version to avoid async context issues.
        
        Requirements: 3.1, 3.2, 5.1, 7.1
        """
        # Simplified validation - just check if user exists and is active
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found or inactive"
            )
        
        # Check for existing active assignment - only prevent same user + same role
        existing_query = select(Assignment).where(
            and_(
                Assignment.entity_type == entity_type,
                Assignment.entity_id == entity_id,
                Assignment.user_id == user_id,
                Assignment.assignment_type == assignment_type,
                Assignment.is_active == True
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing_assignment = existing_result.scalar_one_or_none()
        
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already assigned this role for this entity"
            )
        
        # Always create new assignment (allow multiple users with same role)
        assignment = Assignment(
            id=generate_id("ASSGN"),
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            assignment_type=assignment_type,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        
        # Invalidate caches after all database operations are complete
        try:
            cache_service.clear_pattern("eligible_users")
            cache_service.clear_pattern("assignment_validation")
        except Exception as e:
            # Log cache error but don't fail the assignment
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.error(f"Failed to clear cache after assignment creation: {str(e)}")
        
        # Send assignment notification - temporarily disabled to debug
        try:
            # entity_title = await self._get_entity_title(entity_type, entity_id)
            # project_info = await self._get_project_info(entity_type, entity_id)
            
            # await notification_service.notify_assignment_created(
            #     self.db,
            #     assigned_user_id=user_id,
            #     entity_type=entity_type,
            #     entity_id=entity_id,
            #     entity_title=entity_title,
            #     assigned_by_id=current_user.id,
            #     assignment_type=assignment_type,
            #     project_id=project_info.get("project_id"),
            #     project_name=project_info.get("project_name")
            # )
            pass  # Temporarily disabled
        except Exception as e:
            # Log error but don't fail the assignment
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.error(f"Failed to send assignment notification: {str(e)}")
        
        return assignment
    
    async def unassign_entity(
        self,
        entity_type: str,
        entity_id: str,
        assignment_type: str,
        current_user: User
    ) -> bool:
        """
        Remove assignment from an entity.
        
        Requirements: 5.1, 7.1
        """
        # Find existing assignment
        assignment = await self.get_entity_assignment(
            entity_type, entity_id, assignment_type
        )
        
        if not assignment or not assignment.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        # Create history entry before removing
        await self.create_assignment_history(
            assignment, "unassigned", current_user.id
        )
        
        # Send assignment removal notification - temporarily disabled to debug
        try:
            # entity_title = await self._get_entity_title(entity_type, entity_id)
            # project_info = await self._get_project_info(entity_type, entity_id)
            
            # await notification_service.notify_assignment_removed(
            #     self.db,
            #     removed_user_id=assignment.user_id,
            #     entity_type=entity_type,
            #     entity_id=entity_id,
            #     entity_title=entity_title,
            #     removed_by_id=current_user.id,
            #     assignment_type=assignment_type,
            #     project_id=project_info.get("project_id"),
            #     project_name=project_info.get("project_name")
            # )
            pass  # Temporarily disabled
        except Exception as e:
            # Log error but don't fail the unassignment
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.error(f"Failed to send assignment removal notification: {str(e)}")
        
        # Soft delete the assignment
        assignment.is_active = False
        assignment.updated_by = current_user.id
        
        await self.db.commit()
        
        # Invalidate caches after all database operations are complete
        try:
            cache_service.clear_pattern("eligible_users")
            cache_service.clear_pattern("assignment_validation")
        except Exception as e:
            # Log cache error but don't fail the unassignment
            from app.core.logging import StructuredLogger
            logger = StructuredLogger(__name__)
            logger.error(f"Failed to clear cache after assignment removal: {str(e)}")
        
        return True
    
    async def get_entity_assignments(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[Assignment]:
        """
        Get all assignments for an entity.
        
        Requirements: 8.3, 11.1
        """
        assignments_query = select(Assignment).options(
            selectinload(Assignment.user)
        ).where(
            and_(
                Assignment.entity_type == entity_type,
                Assignment.entity_id == entity_id,
                Assignment.is_active == True
            )
        )
        
        assignments_result = await self.db.execute(assignments_query)
        assignments = assignments_result.scalars().all()
        
        return list(assignments)
    
    async def get_entity_assignment(
        self,
        entity_type: str,
        entity_id: str,
        assignment_type: str
    ) -> Optional[Assignment]:
        """
        Get a specific assignment for an entity.
        """
        assignment_query = select(Assignment).where(
            and_(
                Assignment.entity_type == entity_type,
                Assignment.entity_id == entity_id,
                Assignment.assignment_type == assignment_type,
                Assignment.is_active == True
            )
        )
        
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()
        
        return assignment
    
    async def validate_assignment(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        assignment_type: str
    ) -> Dict[str, Any]:
        """
        Validate assignment rules.
        
        Requirements: 3.1, 4.1, 5.1
        """
        # Get user
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return {"valid": False, "error": "User not found or inactive"}
        
        # Validate role compatibility
        role_validation = self.validate_role_compatibility(
            user, entity_type, assignment_type
        )
        if not role_validation["valid"]:
            return role_validation
        
        # Validate team membership for project-level entities
        if entity_type in ["usecase", "userstory", "task", "subtask"]:
            project_id = await self.get_project_from_entity(entity_type, entity_id)
            if project_id:
                team_validation = await self.validate_team_membership(
                    user_id, project_id
                )
                if not team_validation["valid"]:
                    return team_validation
        
        return {"valid": True}
    
    def validate_role_compatibility(
        self,
        user: User,
        entity_type: str,
        assignment_type: str
    ) -> Dict[str, Any]:
        """
        Validate if user's role is compatible with assignment type.
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
        """
        # Assignment rules matrix
        # Client, Program, Project = Owner (multiple allowed, ANY role can be owner)
        # UseCase, UserStory, Task, Subtask = Assignee from Team Members
        assignment_rules = {
            "client": {
                "owner": []  # Empty list means any role is allowed
            },
            "program": {
                "owner": []  # Empty list means any role is allowed
            },
            "project": {
                "owner": []  # Empty list means any role is allowed
            },
            "usecase": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager", "DevOps"]
            },
            "userstory": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager", "DevOps"]
            },
            "task": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager", "DevOps"]
            },
            "subtask": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager", "DevOps"]
            }
        }
        
        # Check if entity type is valid
        if entity_type not in assignment_rules:
            return {"valid": False, "error": f"Invalid entity type: {entity_type}"}
        
        # Check if assignment type is valid for entity
        if assignment_type not in assignment_rules[entity_type]:
            return {"valid": False, "error": f"Invalid assignment type '{assignment_type}' for entity type '{entity_type}'"}
        
        # Get allowed roles for this assignment
        allowed_roles = assignment_rules[entity_type][assignment_type]
        
        # For owner assignments (client/program/project), allow any role (empty list means no restriction)
        if assignment_type == "owner" and entity_type in ["client", "program", "project"]:
            return {"valid": True}
        
        # Check user's primary role (fallback to role field for backward compatibility)
        user_primary_role = user.primary_role or user.role
        if user_primary_role in allowed_roles:
            return {"valid": True}
        
        # Check user's secondary roles
        if user.secondary_roles:
            for role in user.secondary_roles:
                if role in allowed_roles:
                    return {"valid": True}
        
        # Special case for contact person flag
        if assignment_type == "contact_person" and user.is_contact_person:
            return {"valid": True}
        
        return {
            "valid": False, 
            "error": f"User role '{user_primary_role}' is not compatible with assignment type '{assignment_type}' for entity type '{entity_type}'"
        }
    
    async def validate_team_membership(
        self,
        user_id: str,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Validate if user is a member of the project team.
        
        Requirements: 4.1, 4.2
        """
        # Get project team
        team_query = select(Team).where(
            and_(
                Team.project_id == project_id,
                Team.is_active == True
            )
        )
        team_result = await self.db.execute(team_query)
        team = team_result.scalar_one_or_none()
        
        if not team:
            return {"valid": False, "error": "No active team found for this project"}
        
        # Check if user is a team member
        member_query = select(TeamMember).where(
            and_(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        )
        member_result = await self.db.execute(member_query)
        member = member_result.scalar_one_or_none()
        
        if not member:
            return {"valid": False, "error": "User is not a member of the project team"}
        
        return {"valid": True}
    
    async def get_project_from_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[str]:
        """
        Get the project ID for a given entity.
        
        Requirements: 4.1
        """
        if entity_type == "project":
            return entity_id
        
        # Map entity types to their models and project relationships
        entity_models = {
            "usecase": (Usecase, "project_id"),
            "userstory": (UserStory, "usecase.project_id"),
            "task": (Task, "user_story.usecase.project_id"),
            "subtask": (Subtask, "task.user_story.usecase.project_id")
        }
        
        if entity_type not in entity_models:
            return None
        
        model_class, project_path = entity_models[entity_type]
        
        # For simple direct relationships
        if entity_type == "usecase":
            entity_query = select(model_class).where(model_class.id == entity_id)
            entity_result = await self.db.execute(entity_query)
            entity = entity_result.scalar_one_or_none()
            return entity.project_id if entity else None
        
        # For nested relationships, we need to join tables
        if entity_type == "userstory":
            entity_query = select(UserStory).join(Usecase).where(UserStory.id == entity_id)
            entity_result = await self.db.execute(entity_query)
            entity = entity_result.scalar_one_or_none()
            if entity:
                usecase_query = select(Usecase).where(Usecase.id == entity.usecase_id)
                usecase_result = await self.db.execute(usecase_query)
                usecase = usecase_result.scalar_one_or_none()
                return usecase.project_id if usecase else None
        
        # For task: task -> user_story -> usecase -> project
        if entity_type == "task":
            task_query = select(Task).options(
                selectinload(Task.user_story).selectinload(UserStory.usecase)
            ).where(Task.id == entity_id)
            task_result = await self.db.execute(task_query)
            task = task_result.scalar_one_or_none()
            if task and task.user_story and task.user_story.usecase:
                return task.user_story.usecase.project_id
        
        # For subtask: subtask -> task -> user_story -> usecase -> project  
        if entity_type == "subtask":
            subtask_query = select(Subtask).options(
                selectinload(Subtask.task)
                .selectinload(Task.user_story)
                .selectinload(UserStory.usecase)
            ).where(Subtask.id == entity_id)
            subtask_result = await self.db.execute(subtask_query)
            subtask = subtask_result.scalar_one_or_none()
            if subtask and subtask.task and subtask.task.user_story and subtask.task.user_story.usecase:
                return subtask.task.user_story.usecase.project_id
        
        return None
    
    async def get_eligible_assignees(
        self,
        entity_type: str,
        entity_id: str,
        assignment_type: str
    ) -> List[User]:
        """
        Get list of users eligible for assignment to an entity with caching.
        
        Requirements: 5.1, 6.3, 8.3, 12.1
        """
        # Check cache first
        cache_key = cache_service.eligible_users_key(entity_type, entity_id, assignment_type)
        cached_users = cache_service.get(cache_key)
        if cached_users is not None:
            return cached_users
        
        # Get project ID if applicable
        project_id = None
        if entity_type in ["usecase", "userstory", "task", "subtask"]:
            project_id = await self.get_project_from_entity(entity_type, entity_id)
        
        # Base query for active users
        users_query = select(User).where(User.is_active == True)
        
        # If project-level entity, filter by team membership
        if project_id:
            users_query = users_query.join(TeamMember).join(Team).where(
                and_(
                    Team.project_id == project_id,
                    Team.is_active == True,
                    TeamMember.is_active == True
                )
            )
        
        users_result = await self.db.execute(users_query)
        all_users = users_result.scalars().all()
        
        # For owner assignments on client/program/project, return all active users (no role filtering)
        if assignment_type == "owner" and entity_type in ["client", "program", "project"]:
            eligible_users = list(all_users)
        else:
            # Filter by role compatibility for other assignment types
            eligible_users = []
            for user in all_users:
                role_validation = self.validate_role_compatibility(
                    user, entity_type, assignment_type
                )
                if role_validation["valid"]:
                    eligible_users.append(user)
        
        # Cache the results
        cache_key = cache_service.eligible_users_key(entity_type, entity_id, assignment_type)
        cache_service.set(cache_key, eligible_users)
        
        return eligible_users
    
    async def bulk_assign(
        self,
        assignments: List[Dict[str, str]],
        current_user: User
    ) -> Dict[str, Any]:
        """
        Perform bulk assignment operations.
        
        Requirements: 10.1, 10.2, 10.4
        """
        results = {
            "successful": [],
            "failed": [],
            "total": len(assignments)
        }
        
        for assignment_data in assignments:
            try:
                assignment = await self.assign_entity(
                    entity_type=assignment_data["entity_type"],
                    entity_id=assignment_data["entity_id"],
                    user_id=assignment_data["user_id"],
                    assignment_type=assignment_data["assignment_type"],
                    current_user=current_user
                )
                results["successful"].append({
                    "assignment_id": assignment.id,
                    "entity_type": assignment_data["entity_type"],
                    "entity_id": assignment_data["entity_id"],
                    "user_id": assignment_data["user_id"]
                })
            except Exception as e:
                results["failed"].append({
                    "entity_type": assignment_data["entity_type"],
                    "entity_id": assignment_data["entity_id"],
                    "user_id": assignment_data["user_id"],
                    "error": str(e)
                })
        
        return results
    
    async def create_assignment_history(
        self,
        assignment: Assignment,
        action: str,
        changed_by: str,
        new_user_id: Optional[str] = None
    ) -> AssignmentHistory:
        """
        Create an assignment history entry.
        
        Requirements: 7.1, 7.2
        """
        history = AssignmentHistory(
            id=generate_id("AHIST"),
            assignment_id=assignment.id,
            entity_type=assignment.entity_type,
            entity_id=assignment.entity_id,
            user_id=new_user_id or assignment.user_id,
            assignment_type=assignment.assignment_type,
            action=action,
            previous_user_id=assignment.user_id if new_user_id else None,
            created_by=changed_by
        )
        
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        
        return history
    
    async def get_assignment_history(
        self,
        entity_type: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 50,
        load_users: bool = True
    ) -> List[AssignmentHistory]:
        """
        Get assignment history for an entity with lazy loading and pagination.
        
        Requirements: 7.4, 12.3
        """
        history_query = select(AssignmentHistory)
        
        # Conditionally load user relationships for performance
        if load_users:
            history_query = history_query.options(
                selectinload(AssignmentHistory.user),
                selectinload(AssignmentHistory.previous_user),
                selectinload(AssignmentHistory.creator)
            )
        
        history_query = history_query.where(
            and_(
                AssignmentHistory.entity_type == entity_type,
                AssignmentHistory.entity_id == entity_id
            )
        ).order_by(AssignmentHistory.created_at.desc()).offset(skip).limit(limit)
        
        history_result = await self.db.execute(history_query)
        history = history_result.scalars().all()
        
        return list(history)
    
    async def get_user_assignments(
        self,
        user_id: str,
        entity_type: Optional[str] = None
    ) -> List[Assignment]:
        """
        Get all assignments for a user.
        
        Requirements: 8.3
        """
        assignments_query = select(Assignment).where(
            and_(
                Assignment.user_id == user_id,
                Assignment.is_active == True
            )
        )
        
        if entity_type:
            assignments_query = assignments_query.where(
                Assignment.entity_type == entity_type
            )
        
        assignments_result = await self.db.execute(assignments_query)
        assignments = assignments_result.scalars().all()
        
        return list(assignments)
    
    async def _get_entity_title(self, entity_type: str, entity_id: str) -> Optional[str]:
        """Get the title/name of an entity for notification purposes"""
        try:
            entity_models = {
                'client': (Client, 'name'),
                'program': (Program, 'name'),
                'project': (Project, 'name'),
                'usecase': (Usecase, 'name'),
                'userstory': (UserStory, 'title'),
                'task': (Task, 'title'),
                'subtask': (Subtask, 'title')
            }
            
            if entity_type in entity_models:
                model_class, title_field = entity_models[entity_type]
                result = await self.db.execute(select(model_class).where(model_class.id == entity_id))
                entity = result.scalar_one_or_none()
                if entity:
                    return getattr(entity, title_field, None)
        except Exception:
            pass
        return None
    
    async def _get_project_info(self, entity_type: str, entity_id: str) -> Dict[str, Optional[str]]:
        """Get project information for an entity for notification context"""
        try:
            project_id = await self.get_project_from_entity(entity_type, entity_id)
            if project_id:
                result = await self.db.execute(select(Project).where(Project.id == project_id))
                project = result.scalar_one_or_none()
                return {
                    "project_id": project_id,
                    "project_name": project.name if project else None
                }
        except Exception:
            pass
        return {"project_id": None, "project_name": None}
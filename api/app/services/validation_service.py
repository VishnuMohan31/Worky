"""
Validation Service for assignment rules and business logic validation.
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime

from app.models.team import Team, TeamMember, Assignment
from app.models.user import User
from app.models.hierarchy import Project, Program, Usecase, UserStory, Task, Subtask
from app.models.client import Client


class ValidationResult:
    """Result object for validation operations"""
    
    def __init__(self, valid: bool, error: Optional[str] = None, details: Optional[Dict] = None):
        self.valid = valid
        self.error = error
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "error": self.error,
            "details": self.details
        }


class ConflictInfo:
    """Information about assignment conflicts"""
    
    def __init__(self, conflict_type: str, message: str, existing_assignment: Optional[Assignment] = None):
        self.conflict_type = conflict_type
        self.message = message
        self.existing_assignment = existing_assignment


class ValidationService:
    """Service for validating assignment rules and business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_team_membership(
        self,
        user_id: str,
        project_id: str
    ) -> bool:
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
            return False
        
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
        
        return member is not None
    
    def validate_role_compatibility(
        self,
        user_role: str,
        entity_type: str,
        assignment_type: str
    ) -> bool:
        """
        Validate if user role is compatible with entity type and assignment type.
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
        """
        # Assignment rules matrix
        # Client, Program, Project = Owner (ANY role can be owner)
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
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            },
            "userstory": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            },
            "task": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            },
            "subtask": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            }
        }
        
        # Check if entity type and assignment type are valid
        if entity_type not in assignment_rules:
            return False
        
        if assignment_type not in assignment_rules[entity_type]:
            return False
        
        # For owner assignments (client/program/project), allow any role
        if assignment_type == "owner" and entity_type in ["client", "program", "project"]:
            return True
        
        # Check if user role is allowed for other assignment types
        allowed_roles = assignment_rules[entity_type][assignment_type]
        return user_role in allowed_roles
    
    async def validate_assignment_rules(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        assignment_type: str
    ) -> ValidationResult:
        """
        Comprehensive validation of assignment rules.
        
        Requirements: 3.1, 4.1, 5.1
        """
        # Get user
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            return ValidationResult(False, "User not found")
        
        if not user.is_active:
            return ValidationResult(False, "User is not active")
        
        # Validate role compatibility
        # For owner assignments on client/program/project, any role is allowed (skip validation)
        if not (assignment_type == "owner" and entity_type in ["client", "program", "project"]):
            if not self.validate_role_compatibility(user.primary_role, entity_type, assignment_type):
                # Check secondary roles
                role_compatible = False
                if user.secondary_roles:
                    for role in user.secondary_roles:
                        if self.validate_role_compatibility(role, entity_type, assignment_type):
                            role_compatible = True
                            break
                
                # Special case for contact person
                if assignment_type == "contact_person" and user.is_contact_person:
                    role_compatible = True
                
                if not role_compatible:
                    return ValidationResult(
                        False, 
                        f"User role '{user.primary_role}' is not compatible with assignment type '{assignment_type}' for entity type '{entity_type}'"
                    )
        
        # Validate team membership for project-level entities
        if entity_type in ["usecase", "userstory", "task", "subtask"]:
            project_id = await self.get_project_from_entity(entity_type, entity_id)
            if project_id:
                if not await self.validate_team_membership(user_id, project_id):
                    return ValidationResult(
                        False,
                        "User is not a member of the project team"
                    )
        
        # Validate entity exists
        entity_exists = await self.validate_entity_exists(entity_type, entity_id)
        if not entity_exists:
            return ValidationResult(False, f"Entity {entity_type}:{entity_id} not found")
        
        return ValidationResult(True)
    
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
        
        try:
            if entity_type == "usecase":
                entity_query = select(Usecase).where(Usecase.id == entity_id)
                entity_result = await self.db.execute(entity_query)
                entity = entity_result.scalar_one_or_none()
                return entity.project_id if entity else None
            
            elif entity_type == "userstory":
                entity_query = select(UserStory).options(
                    selectinload(UserStory.usecase)
                ).where(UserStory.id == entity_id)
                entity_result = await self.db.execute(entity_query)
                entity = entity_result.scalar_one_or_none()
                return entity.usecase.project_id if entity and entity.usecase else None
            
            elif entity_type == "task":
                entity_query = select(Task).options(
                    selectinload(Task.user_story).selectinload(UserStory.usecase)
                ).where(Task.id == entity_id)
                entity_result = await self.db.execute(entity_query)
                entity = entity_result.scalar_one_or_none()
                return entity.user_story.usecase.project_id if entity and entity.user_story and entity.user_story.usecase else None
            
            elif entity_type == "subtask":
                entity_query = select(Subtask).options(
                    selectinload(Subtask.task).selectinload(Task.user_story).selectinload(UserStory.usecase)
                ).where(Subtask.id == entity_id)
                entity_result = await self.db.execute(entity_query)
                entity = entity_result.scalar_one_or_none()
                return entity.task.user_story.usecase.project_id if entity and entity.task and entity.task.user_story and entity.task.user_story.usecase else None
        
        except Exception:
            return None
        
        return None
    
    async def validate_entity_exists(
        self,
        entity_type: str,
        entity_id: str
    ) -> bool:
        """
        Validate that an entity exists in the database.
        
        Requirements: 5.1
        """
        entity_models = {
            "client": Client,
            "program": Program,
            "project": Project,
            "usecase": Usecase,
            "userstory": UserStory,
            "task": Task,
            "subtask": Subtask
        }
        
        if entity_type not in entity_models:
            return False
        
        model_class = entity_models[entity_type]
        
        try:
            entity_query = select(model_class).where(model_class.id == entity_id)
            entity_result = await self.db.execute(entity_query)
            entity = entity_result.scalar_one_or_none()
            return entity is not None
        except Exception:
            return False
    
    async def check_assignment_conflicts(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str
    ) -> List[ConflictInfo]:
        """
        Check for assignment conflicts.
        
        Requirements: 5.4
        """
        conflicts = []
        
        # Check for existing assignments of exclusive types (owner, contact_person)
        exclusive_types = ["owner", "contact_person"]
        
        for assignment_type in exclusive_types:
            existing_query = select(Assignment).where(
                and_(
                    Assignment.entity_type == entity_type,
                    Assignment.entity_id == entity_id,
                    Assignment.assignment_type == assignment_type,
                    Assignment.is_active == True
                )
            )
            existing_result = await self.db.execute(existing_query)
            existing_assignment = existing_result.scalar_one_or_none()
            
            if existing_assignment and existing_assignment.user_id != user_id:
                conflicts.append(ConflictInfo(
                    conflict_type="existing_assignment",
                    message=f"Entity already has an active {assignment_type} assignment",
                    existing_assignment=existing_assignment
                ))
        
        return conflicts
    
    async def get_eligible_users_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        assignment_type: str
    ) -> List[User]:
        """
        Get list of users eligible for assignment to a specific entity.
        
        Requirements: 5.1, 6.3
        """
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
            ).distinct()
        
        users_result = await self.db.execute(users_query)
        all_users = users_result.scalars().all()
        
        # For owner assignments on client/program/project, return all active users (no role filtering)
        if assignment_type == "owner" and entity_type in ["client", "program", "project"]:
            return list(all_users)
        
        # Filter by role compatibility for other assignment types
        eligible_users = []
        for user in all_users:
            # Check primary role
            if self.validate_role_compatibility(user.primary_role, entity_type, assignment_type):
                eligible_users.append(user)
                continue
            
            # Check secondary roles
            if user.secondary_roles:
                for role in user.secondary_roles:
                    if self.validate_role_compatibility(role, entity_type, assignment_type):
                        eligible_users.append(user)
                        break
            
            # Special case for contact person
            if assignment_type == "contact_person" and user.is_contact_person:
                eligible_users.append(user)
        
        return eligible_users
    
    async def validate_bulk_assignments(
        self,
        assignments: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Validate a list of assignments for bulk operations.
        
        Requirements: 10.2, 10.4
        """
        results = {
            "valid_assignments": [],
            "invalid_assignments": [],
            "conflicts": [],
            "total": len(assignments)
        }
        
        for i, assignment_data in enumerate(assignments):
            try:
                # Validate required fields
                required_fields = ["entity_type", "entity_id", "user_id", "assignment_type"]
                missing_fields = [field for field in required_fields if field not in assignment_data]
                
                if missing_fields:
                    results["invalid_assignments"].append({
                        "index": i,
                        "assignment": assignment_data,
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    })
                    continue
                
                # Validate assignment rules
                validation_result = await self.validate_assignment_rules(
                    assignment_data["entity_type"],
                    assignment_data["entity_id"],
                    assignment_data["user_id"],
                    assignment_data["assignment_type"]
                )
                
                if validation_result.valid:
                    results["valid_assignments"].append({
                        "index": i,
                        "assignment": assignment_data
                    })
                else:
                    results["invalid_assignments"].append({
                        "index": i,
                        "assignment": assignment_data,
                        "error": validation_result.error
                    })
                
                # Check for conflicts
                conflicts = await self.check_assignment_conflicts(
                    assignment_data["entity_type"],
                    assignment_data["entity_id"],
                    assignment_data["user_id"]
                )
                
                if conflicts:
                    results["conflicts"].extend([{
                        "index": i,
                        "assignment": assignment_data,
                        "conflict": conflict.message
                    } for conflict in conflicts])
            
            except Exception as e:
                results["invalid_assignments"].append({
                    "index": i,
                    "assignment": assignment_data,
                    "error": f"Validation error: {str(e)}"
                })
        
        return results
    
    async def validate_team_access_for_assignment(
        self,
        entity_type: str,
        entity_id: str,
        current_user: User
    ) -> ValidationResult:
        """
        Validate if current user has access to assign entities in the relevant project.
        
        Requirements: 4.1, 4.2
        """
        # Admin users have access to all assignments
        if current_user.primary_role == "Admin":
            return ValidationResult(True)
        
        # For project-level entities, check team membership or project management roles
        if entity_type in ["usecase", "userstory", "task", "subtask"]:
            project_id = await self.get_project_from_entity(entity_type, entity_id)
            if project_id:
                # Check if user is project manager or has management role
                if current_user.primary_role in ["Project Manager", "Architect", "Owner"]:
                    return ValidationResult(True)
                
                # Check if user is a team member with appropriate permissions
                team_member = await self.validate_team_membership(current_user.id, project_id)
                if team_member:
                    return ValidationResult(True)
                
                return ValidationResult(
                    False,
                    "User does not have permission to assign entities in this project"
                )
        
        # For higher-level entities (client, program, project), check role
        if entity_type in ["client", "program", "project"]:
            if current_user.primary_role in ["Admin", "Project Manager", "Architect", "Owner"]:
                return ValidationResult(True)
            
            return ValidationResult(
                False,
                f"User role '{current_user.primary_role}' does not have permission to assign {entity_type} entities"
            )
        
        return ValidationResult(False, "Invalid entity type or insufficient permissions")
    
    def get_assignment_rules_matrix(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get the complete assignment rules matrix.
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
        """
        return {
            "client": {
                "owner": []  # Any role can be owner
            },
            "program": {
                "owner": []  # Any role can be owner
            },
            "project": {
                "owner": []  # Any role can be owner
            },
            "usecase": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            },
            "userstory": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            },
            "task": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            },
            "subtask": {
                "assignee": ["Developer", "Tester", "Designer", "Architect", "Admin", "Owner", "Project Manager", "Lead", "Manager"]
            }
        }
    
    async def validate_project_isolation(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str
    ) -> ValidationResult:
        """
        Validate that project isolation rules are maintained.
        
        Requirements: 4.1, 4.2
        """
        # Get project ID for the entity
        project_id = await self.get_project_from_entity(entity_type, entity_id)
        
        if not project_id:
            # Non-project entities don't have isolation requirements
            return ValidationResult(True)
        
        # Check if user is a member of the project team
        is_team_member = await self.validate_team_membership(user_id, project_id)
        
        if not is_team_member:
            return ValidationResult(
                False,
                "Project isolation violation: User is not a member of the project team"
            )
        
        return ValidationResult(True)
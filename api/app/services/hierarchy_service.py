"""
Hierarchy Service for managing entity creation, updates, and hierarchy operations.
"""
from typing import Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime

from app.models.client import Client
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask, Phase
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate
from app.schemas.hierarchy import (
    ProgramCreate, ProgramUpdate, UsecaseCreate, UsecaseUpdate,
    UserStoryCreate, UserStoryUpdate, SubtaskCreate, SubtaskUpdate
)
from app.schemas.project import ProjectCreate as ProjectCreateSchema, ProjectUpdate
from app.schemas.task import TaskCreate, TaskUpdate

if TYPE_CHECKING:
    from app.schemas.client import ClientUpdate
    from app.schemas.hierarchy import ProgramUpdate, UsecaseUpdate, UserStoryUpdate, SubtaskUpdate
    from app.schemas.project import ProjectUpdate
    from app.schemas.task import TaskUpdate


class HierarchyService:
    """Service for managing hierarchical entities"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== CLIENT OPERATIONS ====================
    
    async def create_client(
        self, 
        client_data: ClientCreate, 
        current_user: User
    ) -> Client:
        """
        Create a new client (Admin only)
        
        Requirements: 1.1, 3.1, 7.1
        """
        # Role check - only Admin can create clients
        if current_user.role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin users can create clients"
            )
        
        # Create client
        client = Client(
            name=client_data.name,
            description=client_data.description,
            is_active=client_data.is_active if hasattr(client_data, 'is_active') else True,
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        
        return client
    
    # ==================== PROGRAM OPERATIONS ====================
    
    async def create_program(
        self, 
        program_data: ProgramCreate, 
        current_user: User
    ) -> Program:
        """
        Create a new program under a client
        
        Requirements: 1.1, 3.1, 7.1
        """
        # Role check - Admin or Architect can create programs
        if current_user.role not in ["Admin", "Architect"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Architect users can create programs"
            )
        
        # Verify client exists and user has access
        client = await self._get_and_verify_client_access(
            program_data.client_id, 
            current_user
        )
        
        # Create program
        program = Program(
            client_id=program_data.client_id,
            name=program_data.name,
            short_description=program_data.short_description,
            long_description=program_data.long_description,
            start_date=program_data.start_date,
            end_date=program_data.end_date,
            status=program_data.status or "Planning",
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(program)
        await self.db.commit()
        await self.db.refresh(program)
        
        return program
    
    # ==================== PROJECT OPERATIONS ====================
    
    async def create_project(
        self, 
        project_data: ProjectCreateSchema, 
        current_user: User
    ) -> Project:
        """
        Create a new project under a program
        
        Requirements: 1.1, 3.1, 7.1
        """
        # Role check - Admin or Architect can create projects
        if current_user.role not in ["Admin", "Architect"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Architect users can create projects"
            )
        
        # Verify program exists and user has access
        program = await self._get_and_verify_program_access(
            project_data.program_id, 
            current_user
        )
        
        # Create project
        project = Project(
            program_id=project_data.program_id,
            name=project_data.name,
            short_description=project_data.short_description,
            long_description=project_data.long_description,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            status=project_data.status or "Planning",
            repository_url=project_data.repository_url,
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    # ==================== USE CASE OPERATIONS ====================
    
    async def create_usecase(
        self, 
        usecase_data: UsecaseCreate, 
        current_user: User
    ) -> Usecase:
        """
        Create a new use case under a project
        
        Requirements: 1.1, 3.1, 7.1
        """
        # Role check - Admin, Architect, or Designer can create use cases
        if current_user.role not in ["Admin", "Architect", "Designer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, Architect, or Designer users can create use cases"
            )
        
        # Verify project exists and user has access
        project = await self._get_and_verify_project_access(
            usecase_data.project_id, 
            current_user
        )
        
        # Create use case
        usecase = Usecase(
            project_id=usecase_data.project_id,
            name=usecase_data.name,
            description=usecase_data.description,
            priority=usecase_data.priority or "Medium",
            status=usecase_data.status or "Draft",
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(usecase)
        await self.db.commit()
        await self.db.refresh(usecase)
        
        return usecase
    
    # ==================== USER STORY OPERATIONS ====================
    
    async def create_user_story(
        self, 
        story_data: UserStoryCreate, 
        current_user: User
    ) -> UserStory:
        """
        Create a new user story under a use case
        
        Requirements: 1.1, 3.1, 7.1
        """
        # Role check - Admin, Architect, or Designer can create user stories
        if current_user.role not in ["Admin", "Architect", "Designer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, Architect, or Designer users can create user stories"
            )
        
        # Verify use case exists and user has access
        usecase = await self._get_and_verify_usecase_access(
            story_data.usecase_id, 
            current_user
        )
        
        # Create user story
        user_story = UserStory(
            usecase_id=story_data.usecase_id,
            title=story_data.title,
            description=story_data.description,
            acceptance_criteria=story_data.acceptance_criteria,
            story_points=story_data.story_points,
            priority=story_data.priority or "Medium",
            status=story_data.status or "Backlog",
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(user_story)
        await self.db.commit()
        await self.db.refresh(user_story)
        
        return user_story
    
    # ==================== TASK OPERATIONS ====================
    
    async def create_task(
        self, 
        task_data: TaskCreate, 
        current_user: User
    ) -> Task:
        """
        Create a new task under a user story with phase validation
        
        Requirements: 1.1, 3.1, 7.1, 10.1
        """
        # Verify user story exists and user has access
        user_story = await self._get_and_verify_user_story_access(
            task_data.user_story_id, 
            current_user
        )
        
        # Note: Phase validation will be added when phase_id is added to TaskCreate schema
        # For now, tasks don't have phase_id in the current schema
        
        # Create task
        task = Task(
            user_story_id=task_data.user_story_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status or "To Do",
            priority=task_data.priority or "Medium",
            assigned_to=task_data.assigned_to,
            estimated_hours=task_data.estimated_hours,
            start_date=task_data.start_date,
            due_date=task_data.due_date,
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    # ==================== SUBTASK OPERATIONS ====================
    
    async def create_subtask(
        self, 
        subtask_data: SubtaskCreate, 
        current_user: User
    ) -> Subtask:
        """
        Create a new subtask under a task with parent task validation
        
        Requirements: 1.1, 3.1, 7.1, 10.1, 10.2
        """
        # Verify parent task exists and user has access
        parent_task = await self._get_and_verify_task_access(
            subtask_data.task_id, 
            current_user
        )
        
        # Validate that parent is a Task, not another Subtask (Requirement 10.2)
        # This is enforced by the schema requiring task_id, which ensures
        # subtasks can only be created under tasks
        
        # Validate phase exists if provided
        if subtask_data.phase_id:
            phase = await self._get_phase(subtask_data.phase_id)
            if not phase:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Phase with ID {subtask_data.phase_id} not found"
                )
        
        # Create subtask
        subtask = Subtask(
            task_id=subtask_data.task_id,
            phase_id=subtask_data.phase_id,
            title=subtask_data.title,
            description=subtask_data.description,
            status=subtask_data.status or "To Do",
            assigned_to=subtask_data.assigned_to,
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(subtask)
        await self.db.commit()
        await self.db.refresh(subtask)
        
        return subtask
    
    # ==================== HELPER METHODS ====================
    
    async def _get_and_verify_client_access(
        self, 
        client_id: UUID, 
        current_user: User
    ) -> Client:
        """Verify client exists and user has access"""
        result = await self.db.execute(
            select(Client).where(
                Client.id == client_id,
                Client.is_deleted == False
            )
        )
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found"
            )
        
        # Client-level data isolation (Requirement 3.1)
        if current_user.role != "Admin" and current_user.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access entities within your client"
            )
        
        return client
    
    async def _get_and_verify_program_access(
        self, 
        program_id: UUID, 
        current_user: User
    ) -> Program:
        """Verify program exists and user has access"""
        result = await self.db.execute(
            select(Program).where(
                Program.id == program_id,
                Program.is_deleted == False
            )
        )
        program = result.scalar_one_or_none()
        
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
        
        # Verify client-level access
        await self._get_and_verify_client_access(program.client_id, current_user)
        
        return program
    
    async def _get_and_verify_project_access(
        self, 
        project_id: UUID, 
        current_user: User
    ) -> Project:
        """Verify project exists and user has access"""
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.is_deleted == False
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Verify program and client-level access
        await self._get_and_verify_program_access(project.program_id, current_user)
        
        return project
    
    async def _get_and_verify_usecase_access(
        self, 
        usecase_id: UUID, 
        current_user: User
    ) -> Usecase:
        """Verify use case exists and user has access"""
        result = await self.db.execute(
            select(Usecase).where(
                Usecase.id == usecase_id,
                Usecase.is_deleted == False
            )
        )
        usecase = result.scalar_one_or_none()
        
        if not usecase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Use case with ID {usecase_id} not found"
            )
        
        # Verify project and client-level access
        await self._get_and_verify_project_access(usecase.project_id, current_user)
        
        return usecase
    
    async def _get_and_verify_user_story_access(
        self, 
        user_story_id: UUID, 
        current_user: User
    ) -> UserStory:
        """Verify user story exists and user has access"""
        result = await self.db.execute(
            select(UserStory).where(
                UserStory.id == user_story_id,
                UserStory.is_deleted == False
            )
        )
        user_story = result.scalar_one_or_none()
        
        if not user_story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User story with ID {user_story_id} not found"
            )
        
        # Verify use case and client-level access
        await self._get_and_verify_usecase_access(user_story.usecase_id, current_user)
        
        return user_story
    
    async def _get_and_verify_task_access(
        self, 
        task_id: UUID, 
        current_user: User
    ) -> Task:
        """Verify task exists and user has access"""
        result = await self.db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Verify user story and client-level access
        await self._get_and_verify_user_story_access(task.user_story_id, current_user)
        
        return task
    
    async def _get_phase(self, phase_id: UUID) -> Optional[Phase]:
        """Get phase by ID"""
        result = await self.db.execute(
            select(Phase).where(
                Phase.id == phase_id,
                Phase.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    # ==================== UPDATE OPERATIONS ====================
    
    async def update_client(
        self,
        client_id: UUID,
        client_data: "ClientUpdate",
        current_user: User
    ) -> Client:
        """
        Update a client (Admin only)
        
        Requirements: 4.1, 9.2, 26.4
        """
        # Role check - only Admin can update clients
        if current_user.role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin users can update clients"
            )
        
        # Get and verify access
        client = await self._get_and_verify_client_access(client_id, current_user)
        
        # Update fields
        update_data = client_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        client.updated_by = str(current_user.id)
        client.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(client)
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('client', client_id)
        
        return client
    
    async def update_program(
        self,
        program_id: UUID,
        program_data: "ProgramUpdate",
        current_user: User
    ) -> Program:
        """
        Update a program
        
        Requirements: 4.1, 9.2, 26.4
        """
        # Role check - Admin or Architect can update programs
        if current_user.role not in ["Admin", "Architect"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Architect users can update programs"
            )
        
        # Get and verify access
        program = await self._get_and_verify_program_access(program_id, current_user)
        
        # Update fields
        update_data = program_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(program, field, value)
        
        program.updated_by = str(current_user.id)
        program.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(program)
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('program', program_id)
        
        return program
    
    async def update_project(
        self,
        project_id: UUID,
        project_data: "ProjectUpdate",
        current_user: User
    ) -> Project:
        """
        Update a project
        
        Requirements: 4.1, 9.2, 26.4
        """
        # Role check - Admin or Architect can update projects
        if current_user.role not in ["Admin", "Architect"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Architect users can update projects"
            )
        
        # Get and verify access
        project = await self._get_and_verify_project_access(project_id, current_user)
        
        # Update fields
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_by = str(current_user.id)
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(project)
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('project', project_id)
        
        return project
    
    async def update_usecase(
        self,
        usecase_id: UUID,
        usecase_data: "UsecaseUpdate",
        current_user: User
    ) -> Usecase:
        """
        Update a use case
        
        Requirements: 4.1, 9.2, 26.4
        """
        # Role check - Admin, Architect, or Designer can update use cases
        if current_user.role not in ["Admin", "Architect", "Designer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, Architect, or Designer users can update use cases"
            )
        
        # Get and verify access
        usecase = await self._get_and_verify_usecase_access(usecase_id, current_user)
        
        # Update fields
        update_data = usecase_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(usecase, field, value)
        
        usecase.updated_by = str(current_user.id)
        usecase.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(usecase)
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('usecase', usecase_id)
        
        return usecase
    
    async def update_user_story(
        self,
        user_story_id: UUID,
        story_data: "UserStoryUpdate",
        current_user: User
    ) -> UserStory:
        """
        Update a user story
        
        Requirements: 4.1, 9.2, 26.4
        """
        # Role check - Admin, Architect, or Designer can update user stories
        if current_user.role not in ["Admin", "Architect", "Designer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, Architect, or Designer users can update user stories"
            )
        
        # Get and verify access
        user_story = await self._get_and_verify_user_story_access(user_story_id, current_user)
        
        # Update fields
        update_data = story_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_story, field, value)
        
        user_story.updated_by = str(current_user.id)
        user_story.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user_story)
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('user_story', user_story_id)
        
        return user_story
    
    async def update_task(
        self,
        task_id: UUID,
        task_data: "TaskUpdate",
        current_user: User
    ) -> Task:
        """
        Update a task
        
        Requirements: 4.1, 9.2, 26.4
        """
        # Get and verify access
        task = await self._get_and_verify_task_access(task_id, current_user)
        
        # Developers can only update tasks assigned to them
        if current_user.role == "Developer":
            if task.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Developers can only update tasks assigned to them"
                )
        
        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        task.updated_by = str(current_user.id)
        task.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(task)
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('task', task_id)
        
        return task
    
    async def update_subtask(
        self,
        subtask_id: UUID,
        subtask_data: "SubtaskUpdate",
        current_user: User
    ) -> Subtask:
        """
        Update a subtask
        
        Requirements: 4.1, 9.2, 26.4
        """
        # Get subtask and verify access through parent task
        result = await self.db.execute(
            select(Subtask).where(
                Subtask.id == subtask_id,
                Subtask.is_deleted == False
            )
        )
        subtask = result.scalar_one_or_none()
        
        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subtask with ID {subtask_id} not found"
            )
        
        # Verify access through parent task
        await self._get_and_verify_task_access(subtask.task_id, current_user)
        
        # Developers can only update subtasks assigned to them
        if current_user.role == "Developer":
            if subtask.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Developers can only update subtasks assigned to them"
                )
        
        # Update fields
        update_data = subtask_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subtask, field, value)
        
        subtask.updated_by = str(current_user.id)
        subtask.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(subtask)
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('subtask', subtask_id)
        
        return subtask
    
    # ==================== DELETE OPERATIONS (SOFT DELETE) ====================
    
    async def delete_client(
        self,
        client_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        Soft delete a client (Admin only)
        
        Requirements: 4.1, 9.2, 10.2, 26.4
        """
        # Role check - only Admin can delete clients
        if current_user.role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin users can delete clients"
            )
        
        # Get and verify access
        client = await self._get_and_verify_client_access(client_id, current_user)
        
        # Check for active children (programs)
        await self._check_active_children(client, "programs", "Client")
        
        # Soft delete
        client.is_deleted = True
        client.updated_by = str(current_user.id)
        client.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('client', client_id)
        
        return {"message": f"Client {client.name} has been deleted"}
    
    async def delete_program(
        self,
        program_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        Soft delete a program
        
        Requirements: 4.1, 9.2, 10.2, 26.4
        """
        # Role check - Admin or Architect can delete programs
        if current_user.role not in ["Admin", "Architect"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Architect users can delete programs"
            )
        
        # Get and verify access
        program = await self._get_and_verify_program_access(program_id, current_user)
        
        # Check for active children (projects)
        await self._check_active_children(program, "projects", "Program")
        
        # Soft delete
        program.is_deleted = True
        program.updated_by = str(current_user.id)
        program.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('program', program_id)
        
        return {"message": f"Program {program.name} has been deleted"}
    
    async def delete_project(
        self,
        project_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        Soft delete a project
        
        Requirements: 4.1, 9.2, 10.2, 26.4
        """
        # Role check - Admin or Architect can delete projects
        if current_user.role not in ["Admin", "Architect"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Architect users can delete projects"
            )
        
        # Get and verify access
        project = await self._get_and_verify_project_access(project_id, current_user)
        
        # Check for active children (usecases)
        await self._check_active_children(project, "usecases", "Project")
        
        # Soft delete
        project.is_deleted = True
        project.updated_by = str(current_user.id)
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('project', project_id)
        
        return {"message": f"Project {project.name} has been deleted"}
    
    async def delete_usecase(
        self,
        usecase_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        Soft delete a use case
        
        Requirements: 4.1, 9.2, 10.2, 26.4
        """
        # Role check - Admin, Architect, or Designer can delete use cases
        if current_user.role not in ["Admin", "Architect", "Designer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, Architect, or Designer users can delete use cases"
            )
        
        # Get and verify access
        usecase = await self._get_and_verify_usecase_access(usecase_id, current_user)
        
        # Check for active children (user_stories)
        await self._check_active_children(usecase, "user_stories", "Use case")
        
        # Soft delete
        usecase.is_deleted = True
        usecase.updated_by = str(current_user.id)
        usecase.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('usecase', usecase_id)
        
        return {"message": f"Use case {usecase.name} has been deleted"}
    
    async def delete_user_story(
        self,
        user_story_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        Soft delete a user story
        
        Requirements: 4.1, 9.2, 10.2, 26.4
        """
        # Role check - Admin, Architect, or Designer can delete user stories
        if current_user.role not in ["Admin", "Architect", "Designer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, Architect, or Designer users can delete user stories"
            )
        
        # Get and verify access
        user_story = await self._get_and_verify_user_story_access(user_story_id, current_user)
        
        # Check for active children (tasks)
        await self._check_active_children(user_story, "tasks", "User story")
        
        # Soft delete
        user_story.is_deleted = True
        user_story.updated_by = str(current_user.id)
        user_story.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('user_story', user_story_id)
        
        return {"message": f"User story {user_story.title} has been deleted"}
    
    async def delete_task(
        self,
        task_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        Soft delete a task
        
        Requirements: 4.1, 9.2, 10.2, 26.4
        """
        # Get and verify access
        task = await self._get_and_verify_task_access(task_id, current_user)
        
        # Role check - Admin, Architect, or Designer can delete tasks
        # Developers cannot delete tasks
        if current_user.role == "Developer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Developers cannot delete tasks"
            )
        
        # Check for active children (subtasks)
        await self._check_active_children(task, "subtasks", "Task")
        
        # Soft delete
        task.is_deleted = True
        task.updated_by = str(current_user.id)
        task.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('task', task_id)
        
        return {"message": f"Task {task.title} has been deleted"}
    
    async def delete_subtask(
        self,
        subtask_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        Soft delete a subtask
        
        Requirements: 4.1, 9.2, 10.2, 26.4
        """
        # Get subtask and verify access through parent task
        result = await self.db.execute(
            select(Subtask).where(
                Subtask.id == subtask_id,
                Subtask.is_deleted == False
            )
        )
        subtask = result.scalar_one_or_none()
        
        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subtask with ID {subtask_id} not found"
            )
        
        # Verify access through parent task
        await self._get_and_verify_task_access(subtask.task_id, current_user)
        
        # Role check - Admin, Architect, or Designer can delete subtasks
        # Developers cannot delete subtasks
        if current_user.role == "Developer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Developers cannot delete subtasks"
            )
        
        # Soft delete (subtasks have no children)
        subtask.is_deleted = True
        subtask.updated_by = str(current_user.id)
        subtask.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # TODO: Invalidate cache when CacheService is implemented (Task 5.2)
        # await self.cache.invalidate_entity('subtask', subtask_id)
        
        return {"message": f"Subtask {subtask.title} has been deleted"}
    
    async def _check_active_children(
        self,
        entity: Any,
        children_attr: str,
        entity_type: str
    ) -> None:
        """
        Check if entity has active (non-deleted) children
        
        Requirements: 10.2
        """
        if not hasattr(entity, children_attr):
            return
        
        children = getattr(entity, children_attr)
        active_children = [child for child in children if not child.is_deleted]
        
        if active_children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{entity_type} cannot be deleted because it has {len(active_children)} active child entities. Please delete or archive child entities first."
            )
    
    # ==================== STATISTICS AND ROLLUP OPERATIONS ====================
    
    async def get_entity_statistics(
        self,
        entity_type: str,
        entity_id: UUID,
        current_user: User
    ) -> Dict[str, Any]:
        """
        Get statistics for an entity including status counts, phase distribution, 
        rollup counts, and completion percentage.
        
        Requirements: 8.1, 8.2, 13.1, 13.2, 25.1, 25.2
        """
        # Verify entity exists and user has access
        await self._verify_entity_access(entity_type, entity_id, current_user)
        
        # Get direct children status counts
        status_counts = await self._get_status_counts(entity_type, entity_id)
        
        # Get phase distribution (for User Story and above)
        phase_distribution = None
        if entity_type.lower() in ['userstory', 'usecase', 'project', 'program', 'client']:
            phase_distribution = await self._get_phase_distribution(entity_type, entity_id)
        
        # Get rollup counts (all descendants)
        rollup_counts = await self._get_rollup_counts(entity_type, entity_id)
        
        # Calculate completion percentage
        total = sum(status_counts.values())
        completed = status_counts.get('Completed', 0) + status_counts.get('Done', 0)
        completion_percentage = round((completed / total * 100), 1) if total > 0 else 0.0
        
        return {
            "status_counts": status_counts,
            "phase_distribution": phase_distribution,
            "rollup_counts": rollup_counts,
            "completion_percentage": completion_percentage,
            "total_items": total
        }
    
    async def _get_status_counts(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> Dict[str, int]:
        """
        Get status counts for direct children of an entity.
        
        Requirements: 8.1, 25.1
        """
        from sqlalchemy import func
        
        # Map entity type to child model and parent field
        child_mapping = {
            'client': (Program, 'client_id'),
            'program': (Project, 'program_id'),
            'project': (Usecase, 'project_id'),
            'usecase': (UserStory, 'usecase_id'),
            'userstory': (Task, 'user_story_id'),
            'task': (Subtask, 'task_id')
        }
        
        entity_type_lower = entity_type.lower()
        
        # Subtasks have no children
        if entity_type_lower == 'subtask':
            return {}
        
        if entity_type_lower not in child_mapping:
            return {}
        
        child_model, parent_field = child_mapping[entity_type_lower]
        
        # Query for status counts
        query = select(
            child_model.status,
            func.count(child_model.id).label('count')
        ).where(
            getattr(child_model, parent_field) == entity_id,
            child_model.is_deleted == False
        ).group_by(child_model.status)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # Convert to dictionary
        status_counts = {row.status: row.count for row in rows}
        
        return status_counts
    
    async def _get_phase_distribution(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> list[Dict[str, Any]]:
        """
        Get phase distribution for all descendant tasks and subtasks.
        
        Requirements: 13.1, 13.2, 25.2
        """
        from sqlalchemy import func, or_
        
        # Get all descendant task and subtask IDs
        task_ids = await self._get_descendant_task_ids(entity_type, entity_id)
        
        if not task_ids:
            return []
        
        # Query phase distribution for tasks
        task_query = select(
            Phase.id,
            Phase.name,
            Phase.color,
            func.count(Task.id).label('count')
        ).join(
            Task, Task.phase_id == Phase.id
        ).where(
            Task.id.in_(task_ids),
            Task.is_deleted == False
        ).group_by(Phase.id, Phase.name, Phase.color)
        
        task_result = await self.db.execute(task_query)
        task_rows = task_result.all()
        
        # Query phase distribution for subtasks
        subtask_query = select(
            Phase.id,
            Phase.name,
            Phase.color,
            func.count(Subtask.id).label('count')
        ).join(
            Subtask, Subtask.phase_id == Phase.id
        ).where(
            Subtask.task_id.in_(task_ids),
            Subtask.is_deleted == False
        ).group_by(Phase.id, Phase.name, Phase.color)
        
        subtask_result = await self.db.execute(subtask_query)
        subtask_rows = subtask_result.all()
        
        # Combine task and subtask counts by phase
        phase_counts = {}
        for row in task_rows:
            phase_id = str(row.id)
            if phase_id not in phase_counts:
                phase_counts[phase_id] = {
                    'phase': row.name,
                    'color': row.color,
                    'count': 0
                }
            phase_counts[phase_id]['count'] += row.count
        
        for row in subtask_rows:
            phase_id = str(row.id)
            if phase_id not in phase_counts:
                phase_counts[phase_id] = {
                    'phase': row.name,
                    'color': row.color,
                    'count': 0
                }
            phase_counts[phase_id]['count'] += row.count
        
        # Convert to list and sort by count descending
        distribution = list(phase_counts.values())
        distribution.sort(key=lambda x: x['count'], reverse=True)
        
        return distribution
    
    async def _get_descendant_task_ids(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> list[UUID]:
        """
        Get all descendant task IDs for an entity.
        """
        entity_type_lower = entity_type.lower()
        
        if entity_type_lower == 'task':
            # Entity is a task itself
            return [entity_id]
        
        elif entity_type_lower == 'subtask':
            # Subtasks have no tasks under them
            return []
        
        elif entity_type_lower == 'userstory':
            # Get tasks directly under this user story
            query = select(Task.id).where(
                Task.user_story_id == entity_id,
                Task.is_deleted == False
            )
            result = await self.db.execute(query)
            return [row[0] for row in result.all()]
        
        elif entity_type_lower == 'usecase':
            # Get tasks through user stories
            query = select(Task.id).join(
                UserStory, Task.user_story_id == UserStory.id
            ).where(
                UserStory.usecase_id == entity_id,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            result = await self.db.execute(query)
            return [row[0] for row in result.all()]
        
        elif entity_type_lower == 'project':
            # Get tasks through usecases and user stories
            query = select(Task.id).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).where(
                Usecase.project_id == entity_id,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            result = await self.db.execute(query)
            return [row[0] for row in result.all()]
        
        elif entity_type_lower == 'program':
            # Get tasks through projects, usecases, and user stories
            query = select(Task.id).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).where(
                Project.program_id == entity_id,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            result = await self.db.execute(query)
            return [row[0] for row in result.all()]
        
        elif entity_type_lower == 'client':
            # Get tasks through programs, projects, usecases, and user stories
            query = select(Task.id).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == entity_id,
                Program.is_deleted == False,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            result = await self.db.execute(query)
            return [row[0] for row in result.all()]
        
        return []
    
    async def _get_rollup_counts(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> Dict[str, int]:
        """
        Get counts of all descendant entities by type.
        
        Requirements: 8.2, 25.1, 25.2
        """
        from sqlalchemy import func
        
        entity_type_lower = entity_type.lower()
        counts = {}
        
        if entity_type_lower == 'client':
            # Count programs
            program_query = select(func.count(Program.id)).where(
                Program.client_id == entity_id,
                Program.is_deleted == False
            )
            program_result = await self.db.execute(program_query)
            counts['programs'] = program_result.scalar() or 0
            
            # Count projects
            project_query = select(func.count(Project.id)).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == entity_id,
                Program.is_deleted == False,
                Project.is_deleted == False
            )
            project_result = await self.db.execute(project_query)
            counts['projects'] = project_result.scalar() or 0
            
            # Count usecases
            usecase_query = select(func.count(Usecase.id)).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == entity_id,
                Program.is_deleted == False,
                Project.is_deleted == False,
                Usecase.is_deleted == False
            )
            usecase_result = await self.db.execute(usecase_query)
            counts['usecases'] = usecase_result.scalar() or 0
            
            # Count user stories
            story_query = select(func.count(UserStory.id)).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == entity_id,
                Program.is_deleted == False,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False
            )
            story_result = await self.db.execute(story_query)
            counts['user_stories'] = story_result.scalar() or 0
            
            # Count tasks
            task_query = select(func.count(Task.id)).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == entity_id,
                Program.is_deleted == False,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            task_result = await self.db.execute(task_query)
            counts['tasks'] = task_result.scalar() or 0
            
            # Count subtasks
            subtask_query = select(func.count(Subtask.id)).join(
                Task, Subtask.task_id == Task.id
            ).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == entity_id,
                Program.is_deleted == False,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False,
                Subtask.is_deleted == False
            )
            subtask_result = await self.db.execute(subtask_query)
            counts['subtasks'] = subtask_result.scalar() or 0
        
        elif entity_type_lower == 'program':
            # Count projects
            project_query = select(func.count(Project.id)).where(
                Project.program_id == entity_id,
                Project.is_deleted == False
            )
            project_result = await self.db.execute(project_query)
            counts['projects'] = project_result.scalar() or 0
            
            # Count usecases
            usecase_query = select(func.count(Usecase.id)).join(
                Project, Usecase.project_id == Project.id
            ).where(
                Project.program_id == entity_id,
                Project.is_deleted == False,
                Usecase.is_deleted == False
            )
            usecase_result = await self.db.execute(usecase_query)
            counts['usecases'] = usecase_result.scalar() or 0
            
            # Count user stories
            story_query = select(func.count(UserStory.id)).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).where(
                Project.program_id == entity_id,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False
            )
            story_result = await self.db.execute(story_query)
            counts['user_stories'] = story_result.scalar() or 0
            
            # Count tasks
            task_query = select(func.count(Task.id)).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).where(
                Project.program_id == entity_id,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            task_result = await self.db.execute(task_query)
            counts['tasks'] = task_result.scalar() or 0
            
            # Count subtasks
            subtask_query = select(func.count(Subtask.id)).join(
                Task, Subtask.task_id == Task.id
            ).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).where(
                Project.program_id == entity_id,
                Project.is_deleted == False,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False,
                Subtask.is_deleted == False
            )
            subtask_result = await self.db.execute(subtask_query)
            counts['subtasks'] = subtask_result.scalar() or 0
        
        elif entity_type_lower == 'project':
            # Count usecases
            usecase_query = select(func.count(Usecase.id)).where(
                Usecase.project_id == entity_id,
                Usecase.is_deleted == False
            )
            usecase_result = await self.db.execute(usecase_query)
            counts['usecases'] = usecase_result.scalar() or 0
            
            # Count user stories
            story_query = select(func.count(UserStory.id)).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).where(
                Usecase.project_id == entity_id,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False
            )
            story_result = await self.db.execute(story_query)
            counts['user_stories'] = story_result.scalar() or 0
            
            # Count tasks
            task_query = select(func.count(Task.id)).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).where(
                Usecase.project_id == entity_id,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            task_result = await self.db.execute(task_query)
            counts['tasks'] = task_result.scalar() or 0
            
            # Count subtasks
            subtask_query = select(func.count(Subtask.id)).join(
                Task, Subtask.task_id == Task.id
            ).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).where(
                Usecase.project_id == entity_id,
                Usecase.is_deleted == False,
                UserStory.is_deleted == False,
                Task.is_deleted == False,
                Subtask.is_deleted == False
            )
            subtask_result = await self.db.execute(subtask_query)
            counts['subtasks'] = subtask_result.scalar() or 0
        
        elif entity_type_lower == 'usecase':
            # Count user stories
            story_query = select(func.count(UserStory.id)).where(
                UserStory.usecase_id == entity_id,
                UserStory.is_deleted == False
            )
            story_result = await self.db.execute(story_query)
            counts['user_stories'] = story_result.scalar() or 0
            
            # Count tasks
            task_query = select(func.count(Task.id)).join(
                UserStory, Task.user_story_id == UserStory.id
            ).where(
                UserStory.usecase_id == entity_id,
                UserStory.is_deleted == False,
                Task.is_deleted == False
            )
            task_result = await self.db.execute(task_query)
            counts['tasks'] = task_result.scalar() or 0
            
            # Count subtasks
            subtask_query = select(func.count(Subtask.id)).join(
                Task, Subtask.task_id == Task.id
            ).join(
                UserStory, Task.user_story_id == UserStory.id
            ).where(
                UserStory.usecase_id == entity_id,
                UserStory.is_deleted == False,
                Task.is_deleted == False,
                Subtask.is_deleted == False
            )
            subtask_result = await self.db.execute(subtask_query)
            counts['subtasks'] = subtask_result.scalar() or 0
        
        elif entity_type_lower == 'userstory':
            # Count tasks
            task_query = select(func.count(Task.id)).where(
                Task.user_story_id == entity_id,
                Task.is_deleted == False
            )
            task_result = await self.db.execute(task_query)
            counts['tasks'] = task_result.scalar() or 0
            
            # Count subtasks
            subtask_query = select(func.count(Subtask.id)).join(
                Task, Subtask.task_id == Task.id
            ).where(
                Task.user_story_id == entity_id,
                Task.is_deleted == False,
                Subtask.is_deleted == False
            )
            subtask_result = await self.db.execute(subtask_query)
            counts['subtasks'] = subtask_result.scalar() or 0
        
        elif entity_type_lower == 'task':
            # Count subtasks
            subtask_query = select(func.count(Subtask.id)).where(
                Subtask.task_id == entity_id,
                Subtask.is_deleted == False
            )
            subtask_result = await self.db.execute(subtask_query)
            counts['subtasks'] = subtask_result.scalar() or 0
        
        # Subtask has no children
        
        return counts
    
    async def _verify_entity_access(
        self,
        entity_type: str,
        entity_id: UUID,
        current_user: User
    ) -> None:
        """
        Verify that entity exists and user has access to it.
        """
        entity_type_lower = entity_type.lower()
        
        if entity_type_lower == 'client':
            await self._get_and_verify_client_access(entity_id, current_user)
        elif entity_type_lower == 'program':
            await self._get_and_verify_program_access(entity_id, current_user)
        elif entity_type_lower == 'project':
            await self._get_and_verify_project_access(entity_id, current_user)
        elif entity_type_lower == 'usecase':
            await self._get_and_verify_usecase_access(entity_id, current_user)
        elif entity_type_lower == 'userstory':
            await self._get_and_verify_user_story_access(entity_id, current_user)
        elif entity_type_lower == 'task':
            await self._get_and_verify_task_access(entity_id, current_user)
        elif entity_type_lower == 'subtask':
            # Get subtask and verify through parent task
            result = await self.db.execute(
                select(Subtask).where(
                    Subtask.id == entity_id,
                    Subtask.is_deleted == False
                )
            )
            subtask = result.scalar_one_or_none()
            if not subtask:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Subtask with ID {entity_id} not found"
                )
            await self._get_and_verify_task_access(subtask.task_id, current_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity type: {entity_type}"
            )
    
    # ==================== SEARCH OPERATIONS ====================
    
    async def search_entities(
        self,
        query: str,
        entity_types: Optional[list[str]],
        current_user: User,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Search across all entity types using PostgreSQL full-text search.
        
        Requirements: 2.1, 2.2, 2.3, 6.1, 6.2
        
        Args:
            query: Search query string
            entity_types: Optional list of entity types to search (e.g., ['client', 'program'])
            current_user: Current authenticated user
            page: Page number for pagination (1-indexed)
            page_size: Number of results per page
            
        Returns:
            Dictionary containing search results with pagination info
        """
        from sqlalchemy import or_, func
        
        # Define entity types to search (default to all)
        types_to_search = entity_types or [
            'client', 'program', 'project', 'usecase', 'userstory', 'task', 'subtask'
        ]
        
        # Normalize entity types to lowercase
        types_to_search = [t.lower() for t in types_to_search]
        
        all_results = []
        
        # Search each entity type
        for entity_type in types_to_search:
            entity_results = await self._search_entity_type(
                entity_type, 
                query, 
                current_user
            )
            all_results.extend(entity_results)
        
        # Calculate pagination
        total_results = len(all_results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = all_results[start_idx:end_idx]
        
        # Generate hierarchy paths for paginated results
        for result in paginated_results:
            result['hierarchy_path'] = await self._generate_hierarchy_path(
                result['entity_type'],
                result['id']
            )
        
        return {
            "results": paginated_results,
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_results + page_size - 1) // page_size
        }
    
    async def _search_entity_type(
        self,
        entity_type: str,
        query: str,
        current_user: User
    ) -> list[Dict[str, Any]]:
        """
        Search a specific entity type.
        
        Requirements: 2.1, 2.2, 6.1, 6.2
        """
        from sqlalchemy import or_
        
        # Map entity type to model
        model_mapping = {
            'client': Client,
            'program': Program,
            'project': Project,
            'usecase': Usecase,
            'userstory': UserStory,
            'task': Task,
            'subtask': Subtask
        }
        
        if entity_type not in model_mapping:
            return []
        
        model = model_mapping[entity_type]
        
        # Build search conditions based on model fields
        search_conditions = []
        
        # Search in name/title field
        if hasattr(model, 'name'):
            search_conditions.append(model.name.ilike(f"%{query}%"))
        elif hasattr(model, 'title'):
            search_conditions.append(model.title.ilike(f"%{query}%"))
        
        # Search in description field if it exists
        if hasattr(model, 'description'):
            search_conditions.append(model.description.ilike(f"%{query}%"))
        
        if not search_conditions:
            return []
        
        # Build base query
        search_query = select(model).where(
            or_(*search_conditions),
            model.is_deleted == False
        )
        
        # Apply client-level filtering for non-Admin users (Requirement 6.2)
        if current_user.role != "Admin":
            search_query = await self._apply_client_filter(
                search_query,
                model,
                entity_type,
                current_user.client_id
            )
        
        # Execute query
        result = await self.db.execute(search_query)
        entities = result.scalars().all()
        
        # Convert to result dictionaries
        results = []
        for entity in entities:
            result_dict = {
                "entity_type": entity_type,
                "id": str(entity.id),
                "name": getattr(entity, 'name', None) or getattr(entity, 'title', None),
                "status": getattr(entity, 'status', None),
                "description": getattr(entity, 'description', None)
            }
            results.append(result_dict)
        
        return results
    
    async def _apply_client_filter(
        self,
        query,
        model,
        entity_type: str,
        client_id: UUID
    ):
        """
        Apply client-level filtering to search query for non-Admin users.
        
        Requirements: 6.1, 6.2
        """
        entity_type_lower = entity_type.lower()
        
        if entity_type_lower == 'client':
            # Filter to user's client only
            query = query.where(model.id == client_id)
        
        elif entity_type_lower == 'program':
            # Filter by client_id
            query = query.where(model.client_id == client_id)
        
        elif entity_type_lower == 'project':
            # Join with Program to filter by client
            query = query.join(Program, model.program_id == Program.id).where(
                Program.client_id == client_id,
                Program.is_deleted == False
            )
        
        elif entity_type_lower == 'usecase':
            # Join with Project and Program to filter by client
            query = query.join(
                Project, model.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == client_id,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        
        elif entity_type_lower == 'userstory':
            # Join through Usecase, Project, and Program
            query = query.join(
                Usecase, model.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == client_id,
                Usecase.is_deleted == False,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        
        elif entity_type_lower == 'task':
            # Join through UserStory, Usecase, Project, and Program
            query = query.join(
                UserStory, model.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == client_id,
                UserStory.is_deleted == False,
                Usecase.is_deleted == False,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        
        elif entity_type_lower == 'subtask':
            # Join through Task, UserStory, Usecase, Project, and Program
            query = query.join(
                Task, model.task_id == Task.id
            ).join(
                UserStory, Task.user_story_id == UserStory.id
            ).join(
                Usecase, UserStory.usecase_id == Usecase.id
            ).join(
                Project, Usecase.project_id == Project.id
            ).join(
                Program, Project.program_id == Program.id
            ).where(
                Program.client_id == client_id,
                Task.is_deleted == False,
                UserStory.is_deleted == False,
                Usecase.is_deleted == False,
                Project.is_deleted == False,
                Program.is_deleted == False
            )
        
        return query
    
    async def _generate_hierarchy_path(
        self,
        entity_type: str,
        entity_id: str
    ) -> str:
        """
        Generate hierarchy path string for an entity (e.g., "Client > Program > Project").
        
        Requirements: 2.3
        """
        breadcrumb = await self._get_breadcrumb_for_entity(entity_type, UUID(entity_id))
        
        if not breadcrumb:
            return ""
        
        # Join breadcrumb names with " > "
        path = " > ".join([item['name'] for item in breadcrumb])
        return path
    
    async def _get_breadcrumb_for_entity(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> list[Dict[str, str]]:
        """
        Get breadcrumb trail from Client to current entity.
        
        Requirements: 6.1
        """
        breadcrumb = []
        current_type = entity_type.lower()
        current_id = entity_id
        
        # Traverse up the hierarchy
        while current_type and current_id:
            # Get entity
            entity = await self._get_entity_by_type(current_type, current_id)
            
            if not entity:
                break
            
            # Add to breadcrumb (insert at beginning to maintain order)
            name = getattr(entity, 'name', None) or getattr(entity, 'title', None)
            breadcrumb.insert(0, {
                "type": current_type,
                "id": str(entity.id),
                "name": name
            })
            
            # Move to parent
            parent_info = self._get_parent_info(current_type, entity)
            if not parent_info:
                break
            
            current_type, current_id = parent_info
        
        return breadcrumb
    
    async def _get_entity_by_type(
        self,
        entity_type: str,
        entity_id: UUID
    ):
        """Get entity by type and ID."""
        model_mapping = {
            'client': Client,
            'program': Program,
            'project': Project,
            'usecase': Usecase,
            'userstory': UserStory,
            'task': Task,
            'subtask': Subtask
        }
        
        if entity_type not in model_mapping:
            return None
        
        model = model_mapping[entity_type]
        result = await self.db.execute(
            select(model).where(
                model.id == entity_id,
                model.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    def _get_parent_info(
        self,
        entity_type: str,
        entity
    ) -> Optional[tuple[str, UUID]]:
        """
        Get parent type and ID for an entity.
        
        Returns tuple of (parent_type, parent_id) or None if no parent.
        """
        parent_mapping = {
            'program': ('client', 'client_id'),
            'project': ('program', 'program_id'),
            'usecase': ('project', 'project_id'),
            'userstory': ('usecase', 'usecase_id'),
            'task': ('userstory', 'user_story_id'),
            'subtask': ('task', 'task_id')
        }
        
        if entity_type not in parent_mapping:
            return None
        
        parent_type, parent_field = parent_mapping[entity_type]
        parent_id = getattr(entity, parent_field, None)
        
        if not parent_id:
            return None
        
        return (parent_type, parent_id)

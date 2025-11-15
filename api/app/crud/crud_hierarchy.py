from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask, Phase
from app.schemas.hierarchy import (
    ProgramCreate, ProgramUpdate,
    UsecaseCreate, UsecaseUpdate,
    UserStoryCreate, UserStoryUpdate,
    SubtaskCreate, SubtaskUpdate,
    PhaseCreate, PhaseUpdate
)


class CRUDProgram(CRUDBase[Program, ProgramCreate, ProgramUpdate]):
    async def get_by_client(
        self, 
        db: AsyncSession, 
        *, 
        client_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Program]:
        result = await db.execute(
            select(Program)
            .where(
                Program.client_id == client_id,
                Program.is_deleted == False
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class CRUDProject(CRUDBase[Project, dict, dict]):
    async def get_by_program(
        self, 
        db: AsyncSession, 
        *, 
        program_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Project]:
        result = await db.execute(
            select(Project)
            .where(
                Project.program_id == program_id,
                Project.is_deleted == False
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class CRUDUseCase(CRUDBase[Usecase, UsecaseCreate, UsecaseUpdate]):
    async def get_by_project(
        self, 
        db: AsyncSession, 
        *, 
        project_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Usecase]:
        result = await db.execute(
            select(Usecase)
            .where(
                Usecase.project_id == project_id,
                Usecase.is_deleted == False
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class CRUDUserStory(CRUDBase[UserStory, UserStoryCreate, UserStoryUpdate]):
    async def get_by_usecase(
        self, 
        db: AsyncSession, 
        *, 
        usecase_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserStory]:
        result = await db.execute(
            select(UserStory)
            .where(
                UserStory.usecase_id == usecase_id,
                UserStory.is_deleted == False
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class CRUDTask(CRUDBase[Task, dict, dict]):
    async def get_by_user_story(
        self, 
        db: AsyncSession, 
        *, 
        user_story_id: str, 
        phase_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        query = select(Task).where(
            Task.user_story_id == user_story_id,
            Task.is_deleted == False
        )
        
        if phase_id:
            query = query.where(Task.phase_id == phase_id)
        if status:
            query = query.where(Task.status == status)
            
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()


class CRUDSubtask(CRUDBase[Subtask, SubtaskCreate, SubtaskUpdate]):
    async def get_by_task(
        self, 
        db: AsyncSession, 
        *, 
        task_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Subtask]:
        result = await db.execute(
            select(Subtask)
            .where(
                Subtask.task_id == task_id,
                Subtask.is_deleted == False
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class CRUDPhase(CRUDBase[Phase, PhaseCreate, PhaseUpdate]):
    async def get_active(self, db: AsyncSession) -> List[Phase]:
        result = await db.execute(
            select(Phase)
            .where(
                Phase.is_deleted == False
            )
            .order_by(Phase.order)
        )
        return result.scalars().all()


# Create instances
program = CRUDProgram(Program)
project = CRUDProject(Project)
usecase = CRUDUseCase(Usecase)
user_story = CRUDUserStory(UserStory)
task = CRUDTask(Task)
subtask = CRUDSubtask(Subtask)
phase = CRUDPhase(Phase)

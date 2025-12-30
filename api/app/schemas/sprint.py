from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class SprintBase(BaseModel):
    project_id: str
    name: str
    goal: Optional[str] = None
    start_date: date
    end_date: date
    status: str = "Planning"


class SprintCreate(SprintBase):
    pass


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class SprintResponse(SprintBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SprintWithTasks(SprintResponse):
    task_count: Optional[int] = 0
    completed_task_count: Optional[int] = 0
    in_progress_task_count: Optional[int] = 0
    todo_task_count: Optional[int] = 0


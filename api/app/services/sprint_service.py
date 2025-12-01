from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.sprint import Sprint
from app.models.hierarchy import Project, Task


class SprintService:
    """Service for managing sprints and sprint generation"""
    
    DAYS_OF_WEEK = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    
    @staticmethod
    def get_next_weekday(start_date: date, target_day: str) -> date:
        """Get the next occurrence of target_day starting from start_date"""
        target_weekday = SprintService.DAYS_OF_WEEK.get(target_day, 0)
        days_ahead = target_weekday - start_date.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    
    @staticmethod
    def calculate_sprint_dates(start_date: date, length_weeks: int, starting_day: str) -> tuple:
        """Calculate sprint start and end dates"""
        # Get the next occurrence of starting_day
        sprint_start = SprintService.get_next_weekday(start_date, starting_day)
        # Calculate end date (one day before the next starting_day)
        sprint_end = sprint_start + timedelta(weeks=length_weeks) - timedelta(days=1)
        return sprint_start, sprint_end
    
    @staticmethod
    async def get_or_create_sprint_config(db: AsyncSession, project_id: str) -> tuple[str, str]:
        """Get sprint configuration from project, return defaults if not set"""
        from app.models.hierarchy import Project
        
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if project:
            length_weeks = project.sprint_length_weeks or "2"
            starting_day = project.sprint_starting_day or "Monday"
        else:
            length_weeks = "2"
            starting_day = "Monday"
        
        return length_weeks, starting_day
    
    @staticmethod
    async def ensure_future_sprints(
        db: AsyncSession,
        project_id: str,
        client_id: str = None,  # Kept for backward compatibility but not used
        min_sprints: int = 6,
        regenerate_from_date: Optional[date] = None
    ) -> List[Sprint]:
        """Ensure at least min_sprints sprints exist in the future for a project
        
        Args:
            regenerate_from_date: If provided, delete all sprints starting from this date
                                 and regenerate them. Used when sprint config changes.
        """
        # Get sprint configuration from project
        length_weeks, starting_day = await SprintService.get_or_create_sprint_config(db, project_id)
        length_weeks_int = int(length_weeks)
        
        # If regenerate_from_date is provided, delete all sprints from that date onwards
        if regenerate_from_date:
            result = await db.execute(
                select(Sprint).where(
                    Sprint.project_id == project_id,
                    Sprint.start_date >= regenerate_from_date
                )
            )
            sprints_to_delete = result.scalars().all()
            for sprint in sprints_to_delete:
                await db.delete(sprint)
            await db.commit()
        
        # Get the latest sprint for this project (after potential deletion)
        result = await db.execute(
            select(Sprint)
            .where(Sprint.project_id == project_id)
            .order_by(Sprint.start_date.desc())
            .limit(1)
        )
        latest_sprint = result.scalar_one_or_none()
        
        # Determine start date for new sprints
        if latest_sprint:
            # Start from the day after the latest sprint ends, but not before today
            candidate_start = latest_sprint.end_date + timedelta(days=1)
            next_start_date = max(candidate_start, date.today())
        else:
            # No sprints exist, start from today
            next_start_date = date.today()
        
        # Generate sprints
        created_sprints = []
        current_date = next_start_date
        
        # Get existing sprints to check what we need to create
        result = await db.execute(
            select(Sprint)
            .where(Sprint.project_id == project_id)
            .order_by(Sprint.start_date.asc())
        )
        existing_sprints = result.scalars().all()
        
        # Calculate how many sprints we need
        future_sprints = [s for s in existing_sprints if s.end_date >= date.today()]
        sprints_needed = max(0, min_sprints - len(future_sprints))
        
        for i in range(sprints_needed):
            sprint_start, sprint_end = SprintService.calculate_sprint_dates(
                current_date, length_weeks_int, starting_day
            )
            
            # Check if this sprint already exists
            result = await db.execute(
                select(Sprint).where(
                    Sprint.project_id == project_id,
                    Sprint.start_date == sprint_start,
                    Sprint.end_date == sprint_end
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                # Create new sprint
                sprint_number = len(existing_sprints) + len(created_sprints) + 1
                new_sprint = Sprint(
                    project_id=project_id,
                    name=f"Sprint {sprint_number}",
                    start_date=sprint_start,
                    end_date=sprint_end,
                    status="Planning"
                )
                db.add(new_sprint)
                created_sprints.append(new_sprint)
            
            # Move to next sprint start date
            current_date = sprint_end + timedelta(days=1)
        
        if created_sprints:
            await db.commit()
            for sprint in created_sprints:
                await db.refresh(sprint)
        
        # Return all future sprints
        result = await db.execute(
            select(Sprint)
            .where(Sprint.project_id == project_id)
            .where(Sprint.end_date >= date.today())
            .order_by(Sprint.start_date.asc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_project_sprints(
        db: AsyncSession,
        project_id: str,
        include_past: bool = False
    ) -> List[Sprint]:
        """Get all sprints for a project"""
        query = select(Sprint).where(Sprint.project_id == project_id)
        
        if not include_past:
            query = query.where(Sprint.end_date >= date.today())
        
        query = query.order_by(Sprint.start_date.asc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_sprint_with_stats(
        db: AsyncSession,
        sprint_id: str
    ) -> Optional[dict]:
        """Get sprint with task statistics"""
        result = await db.execute(
            select(Sprint).where(Sprint.id == sprint_id)
        )
        sprint = result.scalar_one_or_none()
        
        if not sprint:
            return None
        
        # Get task counts
        total_tasks_result = await db.execute(
            select(func.count(Task.id))
            .where(Task.sprint_id == sprint_id, Task.is_deleted == False)
        )
        total_tasks = total_tasks_result.scalar() or 0
        
        completed_tasks_result = await db.execute(
            select(func.count(Task.id))
            .where(
                Task.sprint_id == sprint_id,
                Task.status == "Done",
                Task.is_deleted == False
            )
        )
        completed_tasks = completed_tasks_result.scalar() or 0
        
        in_progress_tasks_result = await db.execute(
            select(func.count(Task.id))
            .where(
                Task.sprint_id == sprint_id,
                Task.status == "In Progress",
                Task.is_deleted == False
            )
        )
        in_progress_tasks = in_progress_tasks_result.scalar() or 0
        
        todo_tasks_result = await db.execute(
            select(func.count(Task.id))
            .where(
                Task.sprint_id == sprint_id,
                Task.status == "To Do",
                Task.is_deleted == False
            )
        )
        todo_tasks = todo_tasks_result.scalar() or 0
        
        return {
            "sprint": sprint,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "todo_tasks": todo_tasks
        }


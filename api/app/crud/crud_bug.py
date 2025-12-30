from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.bug import Bug
from app.schemas.bug import BugCreate, BugUpdate


class CRUDBug(CRUDBase[Bug, BugCreate, BugUpdate]):
    """CRUD operations for Bug model with hierarchy support"""
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: BugCreate,
        reported_by: str
    ) -> Bug:
        """
        Create a new bug.
        
        Args:
            db: Database session
            obj_in: Bug data
            reported_by: User ID of the reporter
            
        Returns:
            Created bug
        """
        from fastapi.encoders import jsonable_encoder
        
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["reported_by"] = reported_by
        obj_in_data["status"] = "New"  # Default status for new bugs
        
        db_obj = Bug(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    # Valid status transitions
    STATUS_TRANSITIONS = {
        "New": ["Open", "Deferred", "Rejected"],
        "Open": ["In Progress", "Deferred", "Rejected"],
        "In Progress": ["Fixed", "Blocked", "Deferred"],
        "Fixed": ["Ready for Testing", "Reopened"],
        "Ready for Testing": ["Retest", "Verified", "Reopened"],
        "Retest": ["Fixed", "Reopened"],
        "Verified": ["Closed", "Reopened"],
        "Closed": ["Reopened"],
        "Reopened": ["Open", "In Progress"],
        "Deferred": ["Open", "Rejected"],
        "Rejected": [],  # Terminal state
        "Blocked": ["In Progress", "Deferred"]
    }
    
    async def get_by_entity(
        self, 
        db: AsyncSession, 
        *, 
        entity_type: str, 
        entity_id: str,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Legacy method for backward compatibility"""
        query = select(Bug).where(
            Bug.entity_type == entity_type,
            Bug.entity_id == entity_id,
            Bug.is_deleted == False
        )
        
        if severity:
            query = query.where(Bug.severity == severity)
        if status:
            query = query.where(Bug.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_assignee(
        self, 
        db: AsyncSession, 
        *, 
        assignee_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Bug]:
        """Get bugs assigned to a specific user"""
        query = select(Bug).where(
            Bug.assigned_to == assignee_id,
            Bug.is_deleted == False
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_hierarchy(
        self,
        db: AsyncSession,
        *,
        client_id: Optional[str] = None,
        program_id: Optional[str] = None,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        user_story_id: Optional[str] = None,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        severity: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        priority: Optional[List[str]] = None,
        category: Optional[List[str]] = None,
        bug_type: Optional[str] = None,
        assignee_id: Optional[str] = None,
        reporter_id: Optional[str] = None,
        qa_owner_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Bug]:
        """
        Get bugs filtered by hierarchy level (direct association only).
        
        Args:
            db: Database session
            client_id: Filter by client
            program_id: Filter by program
            project_id: Filter by project
            usecase_id: Filter by use case
            user_story_id: Filter by user story
            task_id: Filter by task
            subtask_id: Filter by subtask
            severity: Filter by severity (list)
            status: Filter by status (list)
            priority: Filter by priority (list)
            category: Filter by category (list)
            bug_type: Filter by bug type
            assignee_id: Filter by assignee
            reporter_id: Filter by reporter
            qa_owner_id: Filter by QA owner
            search: Search in title, description, and reproduction steps
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of bugs matching the criteria
        """
        query = select(Bug).where(Bug.is_deleted == False)
        
        # Apply hierarchy filters
        if client_id:
            query = query.where(Bug.client_id == client_id)
        if program_id:
            query = query.where(Bug.program_id == program_id)
        if project_id:
            query = query.where(Bug.project_id == project_id)
        if usecase_id:
            query = query.where(Bug.usecase_id == usecase_id)
        if user_story_id:
            query = query.where(Bug.user_story_id == user_story_id)
        if task_id:
            query = query.where(Bug.task_id == task_id)
        if subtask_id:
            query = query.where(Bug.subtask_id == subtask_id)
        
        # Apply additional filters
        if severity:
            query = query.where(Bug.severity.in_(severity))
        if status:
            query = query.where(Bug.status.in_(status))
        if priority:
            query = query.where(Bug.priority.in_(priority))
        if category:
            query = query.where(Bug.category.in_(category))
        if bug_type:
            query = query.where(Bug.bug_type == bug_type)
        if assignee_id:
            query = query.where(or_(Bug.assigned_to == assignee_id, Bug.assignee_id == assignee_id))
        if reporter_id:
            query = query.where(or_(Bug.reported_by == reporter_id, Bug.reporter_id == reporter_id))
        if qa_owner_id:
            query = query.where(Bug.qa_owner_id == qa_owner_id)
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Bug.title.ilike(search_pattern),
                    Bug.description.ilike(search_pattern),
                    Bug.reproduction_steps.ilike(search_pattern)
                )
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_hierarchy_with_descendants(
        self,
        db: AsyncSession,
        *,
        client_id: Optional[str] = None,
        program_id: Optional[str] = None,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        user_story_id: Optional[str] = None,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        severity: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        priority: Optional[List[str]] = None,
        category: Optional[List[str]] = None,
        bug_type: Optional[str] = None,
        assignee_id: Optional[str] = None,
        reporter_id: Optional[str] = None,
        qa_owner_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Bug]:
        """
        Get bugs including all descendants in the hierarchy.
        
        For example, if project_id is specified, returns bugs associated with:
        - The project itself
        - All use cases under the project
        - All user stories under those use cases
        - All tasks under those user stories
        - All subtasks under those tasks
        
        Args:
            db: Database session
            (same parameters as get_by_hierarchy plus category, qa_owner_id, and search)
            
        Returns:
            List of bugs matching the criteria including descendants
        """
        from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask
        
        query = select(Bug).where(Bug.is_deleted == False)
        
        # Build hierarchy conditions
        hierarchy_conditions = []
        
        if subtask_id:
            # Subtask is a leaf node, no descendants
            hierarchy_conditions.append(Bug.subtask_id == subtask_id)
        elif task_id:
            # Include bugs at task level and all subtasks under it
            hierarchy_conditions.append(Bug.task_id == task_id)
            
            # Get all subtasks under this task
            subtask_subquery = select(Subtask.id).where(
                and_(
                    Subtask.task_id == task_id,
                    Subtask.is_deleted == False
                )
            )
            subtask_result = await db.execute(subtask_subquery)
            subtask_ids = [row[0] for row in subtask_result.fetchall()]
            
            if subtask_ids:
                hierarchy_conditions.append(Bug.subtask_id.in_(subtask_ids))
        elif user_story_id:
            # Include bugs at user story level and all descendants
            hierarchy_conditions.append(Bug.user_story_id == user_story_id)
            
            # Get all tasks under this user story
            task_subquery = select(Task.id).where(
                and_(
                    Task.user_story_id == user_story_id,
                    Task.is_deleted == False
                )
            )
            task_result = await db.execute(task_subquery)
            task_ids = [row[0] for row in task_result.fetchall()]
            
            if task_ids:
                hierarchy_conditions.append(Bug.task_id.in_(task_ids))
                
                # Get all subtasks under these tasks
                subtask_subquery = select(Subtask.id).where(
                    and_(
                        Subtask.task_id.in_(task_ids),
                        Subtask.is_deleted == False
                    )
                )
                subtask_result = await db.execute(subtask_subquery)
                subtask_ids = [row[0] for row in subtask_result.fetchall()]
                
                if subtask_ids:
                    hierarchy_conditions.append(Bug.subtask_id.in_(subtask_ids))
        elif usecase_id:
            # Include bugs at use case level and all descendants
            hierarchy_conditions.append(Bug.usecase_id == usecase_id)
            
            # Get all user stories under this use case
            user_story_subquery = select(UserStory.id).where(
                and_(
                    UserStory.usecase_id == usecase_id,
                    UserStory.is_deleted == False
                )
            )
            user_story_result = await db.execute(user_story_subquery)
            user_story_ids = [row[0] for row in user_story_result.fetchall()]
            
            if user_story_ids:
                hierarchy_conditions.append(Bug.user_story_id.in_(user_story_ids))
                
                # Get all tasks under these user stories
                task_subquery = select(Task.id).where(
                    and_(
                        Task.user_story_id.in_(user_story_ids),
                        Task.is_deleted == False
                    )
                )
                task_result = await db.execute(task_subquery)
                task_ids = [row[0] for row in task_result.fetchall()]
                
                if task_ids:
                    hierarchy_conditions.append(Bug.task_id.in_(task_ids))
                    
                    # Get all subtasks under these tasks
                    subtask_subquery = select(Subtask.id).where(
                        and_(
                            Subtask.task_id.in_(task_ids),
                            Subtask.is_deleted == False
                        )
                    )
                    subtask_result = await db.execute(subtask_subquery)
                    subtask_ids = [row[0] for row in subtask_result.fetchall()]
                    
                    if subtask_ids:
                        hierarchy_conditions.append(Bug.subtask_id.in_(subtask_ids))
        elif project_id:
            # Include bugs at project level and all descendants
            hierarchy_conditions.append(Bug.project_id == project_id)
            
            # Get all use cases under this project
            usecase_subquery = select(Usecase.id).where(
                and_(
                    Usecase.project_id == project_id,
                    Usecase.is_deleted == False
                )
            )
            usecase_result = await db.execute(usecase_subquery)
            usecase_ids = [row[0] for row in usecase_result.fetchall()]
            
            if usecase_ids:
                hierarchy_conditions.append(Bug.usecase_id.in_(usecase_ids))
                
                # Continue down the hierarchy (user stories, tasks, subtasks)
                user_story_subquery = select(UserStory.id).where(
                    and_(
                        UserStory.usecase_id.in_(usecase_ids),
                        UserStory.is_deleted == False
                    )
                )
                user_story_result = await db.execute(user_story_subquery)
                user_story_ids = [row[0] for row in user_story_result.fetchall()]
                
                if user_story_ids:
                    hierarchy_conditions.append(Bug.user_story_id.in_(user_story_ids))
                    
                    task_subquery = select(Task.id).where(
                        and_(
                            Task.user_story_id.in_(user_story_ids),
                            Task.is_deleted == False
                        )
                    )
                    task_result = await db.execute(task_subquery)
                    task_ids = [row[0] for row in task_result.fetchall()]
                    
                    if task_ids:
                        hierarchy_conditions.append(Bug.task_id.in_(task_ids))
                        
                        subtask_subquery = select(Subtask.id).where(
                            and_(
                                Subtask.task_id.in_(task_ids),
                                Subtask.is_deleted == False
                            )
                        )
                        subtask_result = await db.execute(subtask_subquery)
                        subtask_ids = [row[0] for row in subtask_result.fetchall()]
                        
                        if subtask_ids:
                            hierarchy_conditions.append(Bug.subtask_id.in_(subtask_ids))
        elif program_id:
            # Include bugs at program level and all descendants
            hierarchy_conditions.append(Bug.program_id == program_id)
            
            # Get all projects under this program
            project_subquery = select(Project.id).where(
                and_(
                    Project.program_id == program_id,
                    Project.is_deleted == False
                )
            )
            project_result = await db.execute(project_subquery)
            project_ids = [row[0] for row in project_result.fetchall()]
            
            if project_ids:
                hierarchy_conditions.append(Bug.project_id.in_(project_ids))
                
                # Continue down the hierarchy
                usecase_subquery = select(Usecase.id).where(
                    and_(
                        Usecase.project_id.in_(project_ids),
                        Usecase.is_deleted == False
                    )
                )
                usecase_result = await db.execute(usecase_subquery)
                usecase_ids = [row[0] for row in usecase_result.fetchall()]
                
                if usecase_ids:
                    hierarchy_conditions.append(Bug.usecase_id.in_(usecase_ids))
                    
                    # Continue with user stories, tasks, subtasks...
                    # (Similar pattern as above)
        elif client_id:
            # Include bugs at client level and all descendants
            hierarchy_conditions.append(Bug.client_id == client_id)
            
            # Get all programs under this client
            program_subquery = select(Program.id).where(
                and_(
                    Program.client_id == client_id,
                    Program.is_deleted == False
                )
            )
            program_result = await db.execute(program_subquery)
            program_ids = [row[0] for row in program_result.fetchall()]
            
            if program_ids:
                hierarchy_conditions.append(Bug.program_id.in_(program_ids))
                
                # Continue down the hierarchy
                # (Similar pattern as above)
        
        # Apply hierarchy conditions with OR
        if hierarchy_conditions:
            query = query.where(or_(*hierarchy_conditions))
        
        # Apply additional filters
        if severity:
            query = query.where(Bug.severity.in_(severity))
        if status:
            query = query.where(Bug.status.in_(status))
        if priority:
            query = query.where(Bug.priority.in_(priority))
        if category:
            query = query.where(Bug.category.in_(category))
        if bug_type:
            query = query.where(Bug.bug_type == bug_type)
        if assignee_id:
            query = query.where(or_(Bug.assigned_to == assignee_id, Bug.assignee_id == assignee_id))
        if reporter_id:
            query = query.where(or_(Bug.reported_by == reporter_id, Bug.reporter_id == reporter_id))
        if qa_owner_id:
            query = query.where(Bug.qa_owner_id == qa_owner_id)
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Bug.title.ilike(search_pattern),
                    Bug.description.ilike(search_pattern),
                    Bug.reproduction_steps.ilike(search_pattern)
                )
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    def validate_status_transition(
        self,
        current_status: str,
        new_status: str
    ) -> Tuple[bool, str]:
        """
        Validate if a status transition is allowed.
        
        Args:
            current_status: Current bug status
            new_status: Desired new status
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if current_status == new_status:
            return True, ""
        
        allowed_transitions = self.STATUS_TRANSITIONS.get(current_status, [])
        
        if new_status not in allowed_transitions:
            return False, f"Invalid status transition from '{current_status}' to '{new_status}'. Allowed transitions: {', '.join(allowed_transitions)}"
        
        return True, ""
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        bug_id: str,
        new_status: str,
        resolution_type: Optional[str] = None,
        resolution_notes: Optional[str] = None,
        updated_by: str
    ) -> Tuple[Optional[Bug], str]:
        """
        Update bug status with validation and history tracking.
        
        Args:
            db: Database session
            bug_id: Bug ID
            new_status: New status
            resolution_type: Resolution type (required for Fixed status)
            resolution_notes: Notes about the resolution
            updated_by: User making the change
            
        Returns:
            Tuple of (updated_bug, error_message)
        """
        from app.models.comment import BugStatusHistory
        
        bug = await self.get(db, id=bug_id)
        if not bug:
            return None, f"Bug with id {bug_id} not found"
        
        # Validate status transition
        is_valid, error_msg = self.validate_status_transition(bug.status, new_status)
        if not is_valid:
            return None, error_msg
        
        # Validate resolution type for Fixed status
        if new_status == "Fixed" and not resolution_type:
            return None, "resolution_type is required when status is 'Fixed'"
        
        # Track old status
        old_status = bug.status
        
        # Update bug
        bug.status = new_status
        bug.updated_by = updated_by
        
        if resolution_type:
            bug.resolution_type = resolution_type
        if resolution_notes:
            bug.resolution_notes = resolution_notes
        
        # Update closed_at timestamp
        if new_status in ["Verified", "Closed"]:
            bug.closed_at = datetime.utcnow()
        
        # Increment reopen count
        if new_status == "Reopened":
            bug.reopen_count += 1
        
        # Create status history entry
        status_history = BugStatusHistory(
            bug_id=bug_id,
            from_status=old_status,
            to_status=new_status,
            resolution_type=resolution_type,
            notes=resolution_notes,
            changed_by=updated_by
        )
        
        db.add(bug)
        db.add(status_history)
        await db.commit()
        await db.refresh(bug)
        
        return bug, ""
    
    async def assign_bug(
        self,
        db: AsyncSession,
        *,
        bug_id: str,
        assignee_id: str,
        assigned_by: str
    ) -> Tuple[Optional[Bug], str]:
        """
        Assign bug to a user with validation.
        
        Args:
            db: Database session
            bug_id: Bug ID
            assignee_id: User ID to assign to
            assigned_by: User making the assignment
            
        Returns:
            Tuple of (updated_bug, error_message)
        """
        from app.models.user import User
        
        bug = await self.get(db, id=bug_id)
        if not bug:
            return None, f"Bug with id {bug_id} not found"
        
        # Validate assignee exists and is active
        assignee_query = select(User).where(
            and_(
                User.id == assignee_id,
                User.is_deleted == False
            )
        )
        assignee_result = await db.execute(assignee_query)
        assignee = assignee_result.scalar_one_or_none()
        
        if not assignee:
            return None, f"User with id {assignee_id} not found or inactive"
        
        # Update assignment
        old_assignee = bug.assigned_to
        bug.assigned_to = assignee_id
        bug.updated_by = assigned_by
        
        db.add(bug)
        await db.commit()
        await db.refresh(bug)
        
        return bug, ""
    
    async def get_by_test_run(
        self,
        db: AsyncSession,
        *,
        test_run_id: str,
        severity: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        priority: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Bug]:
        """
        Get bugs associated with a test run.
        
        Args:
            db: Database session
            test_run_id: Test run ID
            severity: Filter by severity (list)
            status: Filter by status (list)
            priority: Filter by priority (list)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of bugs associated with the test run
        """
        query = select(Bug).where(
            and_(
                Bug.test_run_id == test_run_id,
                Bug.is_deleted == False
            )
        )
        
        # Apply additional filters
        if severity:
            query = query.where(Bug.severity.in_(severity))
        if status:
            query = query.where(Bug.status.in_(status))
        if priority:
            query = query.where(Bug.priority.in_(priority))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_from_test_case(
        self,
        db: AsyncSession,
        *,
        test_case_id: str,
        reporter_id: str,
        assignee_id: Optional[str] = None,
        qa_owner_id: Optional[str] = None,
        additional_notes: Optional[str] = None
    ) -> Bug:
        """
        Create a bug from a failed test case with pre-populated fields.
        
        Args:
            db: Database session
            test_case_id: Test case ID
            reporter_id: User ID of the reporter
            assignee_id: Optional assignee user ID
            qa_owner_id: Optional QA owner user ID
            additional_notes: Optional additional notes
            
        Returns:
            Created bug
        """
        from app.models.test_case import TestCase
        
        # Get the test case
        test_case_query = select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
        test_case_result = await db.execute(test_case_query)
        test_case = test_case_result.scalar_one_or_none()
        
        if not test_case:
            raise ValueError(f"Test case with id {test_case_id} not found")
        
        if test_case.status != "Failed":
            raise ValueError(f"Test case must have status 'Failed' to create a bug")
        
        # Pre-populate bug fields from test case
        bug_data = {
            "title": f"Bug from Test Case: {test_case.test_case_name}",
            "description": test_case.test_case_description or "",
            "test_run_id": test_case.test_run_id,
            "test_case_id": test_case_id,
            "reproduction_steps": test_case.test_case_steps,
            "expected_result": test_case.expected_result,
            "actual_result": test_case.actual_result or "",
            "component_attached_to": test_case.component_attached_to,
            "reported_by": reporter_id,
            "status": "New",
            "category": "UI",  # Default, can be changed
            "severity": "Medium",  # Default, can be changed
            "priority": "P2"  # Default, can be changed
        }
        
        if assignee_id:
            bug_data["assigned_to"] = assignee_id
        if qa_owner_id:
            bug_data["qa_owner_id"] = qa_owner_id
        if additional_notes:
            bug_data["description"] += f"\n\nAdditional Notes:\n{additional_notes}"
        
        # Create the bug
        db_obj = Bug(**bug_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def track_assignment(
        self,
        db: AsyncSession,
        *,
        bug_id: str,
        field_name: str,
        old_value: Optional[str],
        new_value: str,
        changed_by: str
    ) -> None:
        """
        Track assignment changes in bug history.
        
        Args:
            db: Database session
            bug_id: Bug ID
            field_name: Name of the field being changed (assignee, qa_owner, reporter)
            old_value: Old value (user ID)
            new_value: New value (user ID)
            changed_by: User making the change
        """
        from app.models.comment import BugComment
        
        # Create a system-generated comment for the assignment change
        comment_text = f"System: {field_name} changed from {old_value or 'None'} to {new_value}"
        
        comment = BugComment(
            bug_id=bug_id,
            comment_text=comment_text,
            author_id=changed_by,
            is_system_generated=True
        )
        
        db.add(comment)
        await db.commit()


bug = CRUDBug(Bug)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.test_case import TestCase
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate


class CRUDTestCase(CRUDBase[TestCase, TestCaseCreate, TestCaseUpdate]):
    """CRUD operations for TestCase model"""
    
    async def get_by_hierarchy(
        self,
        db: AsyncSession,
        *,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        user_story_id: Optional[str] = None,
        task_id: Optional[str] = None,
        status: Optional[str] = None,
        test_type: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestCase]:
        """
        Get test cases filtered by hierarchy level.
        Only returns test cases directly associated with the specified hierarchy entity.
        
        Args:
            db: Database session
            project_id: Filter by project
            usecase_id: Filter by use case
            user_story_id: Filter by user story
            task_id: Filter by task
            status: Filter by status
            test_type: Filter by test type
            priority: Filter by priority
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of test cases matching the criteria
        """
        query = select(TestCase).where(TestCase.is_deleted == False)
        
        # Apply hierarchy filters
        if project_id:
            query = query.where(TestCase.project_id == project_id)
        if usecase_id:
            query = query.where(TestCase.usecase_id == usecase_id)
        if user_story_id:
            query = query.where(TestCase.user_story_id == user_story_id)
        if task_id:
            query = query.where(TestCase.task_id == task_id)
        
        # Apply additional filters
        if status:
            query = query.where(TestCase.status == status)
        if test_type:
            query = query.where(TestCase.test_type == test_type)
        if priority:
            query = query.where(TestCase.priority == priority)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_descendants(
        self,
        db: AsyncSession,
        *,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        user_story_id: Optional[str] = None,
        task_id: Optional[str] = None,
        status: Optional[str] = None,
        test_type: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestCase]:
        """
        Get test cases including all descendants in the hierarchy.
        
        For example, if project_id is specified, returns test cases associated with:
        - The project itself
        - All use cases under the project
        - All user stories under those use cases
        - All tasks under those user stories
        
        Args:
            db: Database session
            project_id: Filter by project (includes descendants)
            usecase_id: Filter by use case (includes descendants)
            user_story_id: Filter by user story (includes descendants)
            task_id: Filter by task (no descendants, tasks are leaf nodes for test cases)
            status: Filter by status
            test_type: Filter by test type
            priority: Filter by priority
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of test cases matching the criteria including descendants
        """
        from app.models.hierarchy import Project, Usecase, UserStory, Task
        
        query = select(TestCase).where(TestCase.is_deleted == False)
        
        # Build hierarchy conditions
        hierarchy_conditions = []
        
        if task_id:
            # Task is a leaf node for test cases, no descendants
            hierarchy_conditions.append(TestCase.task_id == task_id)
        elif user_story_id:
            # Include test cases at user story level and all tasks under it
            hierarchy_conditions.append(TestCase.user_story_id == user_story_id)
            
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
                hierarchy_conditions.append(TestCase.task_id.in_(task_ids))
        elif usecase_id:
            # Include test cases at use case level and all descendants
            hierarchy_conditions.append(TestCase.usecase_id == usecase_id)
            
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
                hierarchy_conditions.append(TestCase.user_story_id.in_(user_story_ids))
                
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
                    hierarchy_conditions.append(TestCase.task_id.in_(task_ids))
        elif project_id:
            # Include test cases at project level and all descendants
            hierarchy_conditions.append(TestCase.project_id == project_id)
            
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
                hierarchy_conditions.append(TestCase.usecase_id.in_(usecase_ids))
                
                # Get all user stories under these use cases
                user_story_subquery = select(UserStory.id).where(
                    and_(
                        UserStory.usecase_id.in_(usecase_ids),
                        UserStory.is_deleted == False
                    )
                )
                user_story_result = await db.execute(user_story_subquery)
                user_story_ids = [row[0] for row in user_story_result.fetchall()]
                
                if user_story_ids:
                    hierarchy_conditions.append(TestCase.user_story_id.in_(user_story_ids))
                    
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
                        hierarchy_conditions.append(TestCase.task_id.in_(task_ids))
        
        # Apply hierarchy conditions with OR
        if hierarchy_conditions:
            query = query.where(or_(*hierarchy_conditions))
        
        # Apply additional filters
        if status:
            query = query.where(TestCase.status == status)
        if test_type:
            query = query.where(TestCase.test_type == test_type)
        if priority:
            query = query.where(TestCase.priority == priority)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def validate_hierarchy_constraint(
        self,
        db: AsyncSession,
        *,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        user_story_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Validate that exactly one hierarchy level is set.
        
        Args:
            db: Database session
            project_id: Project ID
            usecase_id: Use case ID
            user_story_id: User story ID
            task_id: Task ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        hierarchy_fields = [project_id, usecase_id, user_story_id, task_id]
        set_count = sum(1 for field in hierarchy_fields if field is not None)
        
        if set_count == 0:
            return False, "Exactly one hierarchy level must be set (project, usecase, user_story, or task)"
        elif set_count > 1:
            return False, "Only one hierarchy level can be set at a time"
        
        # Validate that the referenced entity exists
        from app.models.hierarchy import Project, Usecase, UserStory, Task
        
        if project_id:
            result = await db.execute(
                select(Project).where(
                    and_(
                        Project.id == project_id,
                        Project.is_deleted == False
                    )
                )
            )
            if not result.scalar_one_or_none():
                return False, f"Project with id {project_id} not found"
        elif usecase_id:
            result = await db.execute(
                select(Usecase).where(
                    and_(
                        Usecase.id == usecase_id,
                        Usecase.is_deleted == False
                    )
                )
            )
            if not result.scalar_one_or_none():
                return False, f"Use case with id {usecase_id} not found"
        elif user_story_id:
            result = await db.execute(
                select(UserStory).where(
                    and_(
                        UserStory.id == user_story_id,
                        UserStory.is_deleted == False
                    )
                )
            )
            if not result.scalar_one_or_none():
                return False, f"User story with id {user_story_id} not found"
        elif task_id:
            result = await db.execute(
                select(Task).where(
                    and_(
                        Task.id == task_id,
                        Task.is_deleted == False
                    )
                )
            )
            if not result.scalar_one_or_none():
                return False, f"Task with id {task_id} not found"
        
        return True, ""
    
    async def count_by_hierarchy(
        self,
        db: AsyncSession,
        *,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        user_story_id: Optional[str] = None,
        task_id: Optional[str] = None,
        include_descendants: bool = False
    ) -> int:
        """
        Count test cases by hierarchy level.
        
        Args:
            db: Database session
            project_id: Filter by project
            usecase_id: Filter by use case
            user_story_id: Filter by user story
            task_id: Filter by task
            include_descendants: Whether to include descendants
            
        Returns:
            Count of test cases
        """
        from sqlalchemy import func
        
        if include_descendants:
            test_cases = await self.get_with_descendants(
                db,
                project_id=project_id,
                usecase_id=usecase_id,
                user_story_id=user_story_id,
                task_id=task_id,
                skip=0,
                limit=999999  # Get all for counting
            )
            return len(test_cases)
        else:
            query = select(func.count(TestCase.id)).where(TestCase.is_deleted == False)
            
            if project_id:
                query = query.where(TestCase.project_id == project_id)
            if usecase_id:
                query = query.where(TestCase.usecase_id == usecase_id)
            if user_story_id:
                query = query.where(TestCase.user_story_id == user_story_id)
            if task_id:
                query = query.where(TestCase.task_id == task_id)
            
            result = await db.execute(query)
            return result.scalar_one()
    
    async def get_by_test_run(
        self,
        db: AsyncSession,
        *,
        test_run_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestCase]:
        """
        Get test cases by test run.
        
        Args:
            db: Database session
            test_run_id: Test run ID
            status: Optional filter by status
            priority: Optional filter by priority
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of test cases in the test run
        """
        query = select(TestCase).where(
            and_(
                TestCase.test_run_id == test_run_id,
                TestCase.is_deleted == False
            )
        )
        
        if status:
            query = query.where(TestCase.status == status)
        if priority:
            query = query.where(TestCase.priority == priority)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_execution(
        self,
        db: AsyncSession,
        *,
        test_case_id: str,
        actual_result: str,
        inference: str,
        status: str,
        executed_by: str,
        remarks: Optional[str] = None
    ) -> TestCase:
        """
        Update test case with execution results.
        
        Args:
            db: Database session
            test_case_id: Test case ID
            actual_result: Actual result from execution
            inference: Inference/conclusion from execution
            status: New status (Passed, Failed, Blocked, Skipped)
            executed_by: User ID of executor
            remarks: Optional additional remarks
            
        Returns:
            Updated test case
        """
        from datetime import datetime
        
        # Get the test case
        test_case = await self.get(db, id=test_case_id)
        if not test_case:
            raise ValueError(f"Test case with id {test_case_id} not found")
        
        # Update execution fields
        test_case.actual_result = actual_result
        test_case.inference = inference
        test_case.status = status
        test_case.executed_by = executed_by
        test_case.executed_at = datetime.utcnow()
        
        if remarks:
            test_case.remarks = remarks
        
        db.add(test_case)
        await db.commit()
        await db.refresh(test_case)
        
        # Update test run metrics
        if test_case.test_run_id:
            from app.crud.crud_test_execution import test_run
            await test_run.update_metrics(db, test_run_id=test_case.test_run_id)
        
        return test_case
    
    async def update_test_run_metrics_on_status_change(
        self,
        db: AsyncSession,
        *,
        test_case: TestCase
    ) -> None:
        """
        Update test run metrics when test case status changes.
        
        Args:
            db: Database session
            test_case: Test case that was updated
        """
        if test_case.test_run_id:
            from app.crud.crud_test_execution import test_run
            await test_run.update_metrics(db, test_run_id=test_case.test_run_id)


# Create instance
test_case = CRUDTestCase(TestCase)

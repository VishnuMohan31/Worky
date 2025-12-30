from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.test_execution import TestExecution, TestRun
from app.schemas.test_execution import (
    TestExecutionCreate, 
    TestRunCreate, 
    TestRunUpdate
)


class CRUDTestExecution(CRUDBase[TestExecution, TestExecutionCreate, dict]):
    """CRUD operations for TestExecution model"""
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: TestExecutionCreate,
        executed_by: str
    ) -> TestExecution:
        """
        Create a new test execution.
        
        Args:
            db: Database session
            obj_in: Test execution data
            executed_by: User ID of the executor
            
        Returns:
            Created test execution
        """
        obj_in_data = obj_in.dict()
        obj_in_data["executed_by"] = executed_by
        
        db_obj = TestExecution(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_test_case(
        self,
        db: AsyncSession,
        *,
        test_case_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestExecution]:
        """
        Get all executions for a specific test case.
        
        Args:
            db: Database session
            test_case_id: Test case ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of test executions ordered by execution date (most recent first)
        """
        query = select(TestExecution).where(
            TestExecution.test_case_id == test_case_id
        ).order_by(TestExecution.execution_date.desc())
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_test_run(
        self,
        db: AsyncSession,
        *,
        test_run_id: str,
        execution_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestExecution]:
        """
        Get all executions for a specific test run.
        
        Args:
            db: Database session
            test_run_id: Test run ID
            execution_status: Optional filter by execution status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of test executions in the test run
        """
        query = select(TestExecution).where(
            TestExecution.test_run_id == test_run_id
        )
        
        if execution_status:
            query = query.where(TestExecution.execution_status == execution_status)
        
        query = query.order_by(TestExecution.execution_date.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_latest_by_test_case(
        self,
        db: AsyncSession,
        *,
        test_case_id: str
    ) -> Optional[TestExecution]:
        """
        Get the most recent execution for a test case.
        
        Args:
            db: Database session
            test_case_id: Test case ID
            
        Returns:
            Most recent test execution or None
        """
        query = select(TestExecution).where(
            TestExecution.test_case_id == test_case_id
        ).order_by(TestExecution.execution_date.desc()).limit(1)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def calculate_metrics(
        self,
        db: AsyncSession,
        *,
        test_case_id: Optional[str] = None,
        test_run_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, any]:
        """
        Calculate execution metrics (pass rate, fail rate, etc.).
        
        Args:
            db: Database session
            test_case_id: Optional filter by test case
            test_run_id: Optional filter by test run
            start_date: Optional filter by start date
            end_date: Optional filter by end date
            
        Returns:
            Dictionary with metrics:
            - total: Total number of executions
            - passed: Number of passed executions
            - failed: Number of failed executions
            - blocked: Number of blocked executions
            - skipped: Number of skipped executions
            - not_applicable: Number of not applicable executions
            - pass_rate: Percentage of passed executions
            - fail_rate: Percentage of failed executions
        """
        query = select(TestExecution)
        
        # Apply filters
        if test_case_id:
            query = query.where(TestExecution.test_case_id == test_case_id)
        if test_run_id:
            query = query.where(TestExecution.test_run_id == test_run_id)
        if start_date:
            query = query.where(TestExecution.execution_date >= start_date)
        if end_date:
            query = query.where(TestExecution.execution_date <= end_date)
        
        result = await db.execute(query)
        executions = result.scalars().all()
        
        total = len(executions)
        passed = sum(1 for e in executions if e.execution_status == "Passed")
        failed = sum(1 for e in executions if e.execution_status == "Failed")
        blocked = sum(1 for e in executions if e.execution_status == "Blocked")
        skipped = sum(1 for e in executions if e.execution_status == "Skipped")
        not_applicable = sum(1 for e in executions if e.execution_status == "Not Applicable")
        
        pass_rate = (passed / total * 100) if total > 0 else 0.0
        fail_rate = (failed / total * 100) if total > 0 else 0.0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "blocked": blocked,
            "skipped": skipped,
            "not_applicable": not_applicable,
            "pass_rate": round(pass_rate, 2),
            "fail_rate": round(fail_rate, 2)
        }
    
    async def get_execution_history(
        self,
        db: AsyncSession,
        *,
        test_case_id: str,
        limit: int = 10
    ) -> List[TestExecution]:
        """
        Get execution history for a test case (most recent first).
        
        Args:
            db: Database session
            test_case_id: Test case ID
            limit: Maximum number of executions to return
            
        Returns:
            List of recent test executions
        """
        return await self.get_by_test_case(
            db,
            test_case_id=test_case_id,
            skip=0,
            limit=limit
        )


class CRUDTestRun(CRUDBase[TestRun, TestRunCreate, TestRunUpdate]):
    """CRUD operations for TestRun model"""
    
    async def get_by_hierarchy(
        self,
        db: AsyncSession,
        *,
        project_id: Optional[str] = None,
        usecase_id: Optional[str] = None,
        user_story_id: Optional[str] = None,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        status: Optional[str] = None,
        run_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestRun]:
        """
        Get test runs filtered by hierarchy level.
        Only returns test runs directly associated with the specified hierarchy entity.
        """
        query = select(TestRun).where(TestRun.is_deleted == False)
        
        # Apply hierarchy filters
        if project_id:
            query = query.where(TestRun.project_id == project_id)
        if usecase_id:
            query = query.where(TestRun.usecase_id == usecase_id)
        if user_story_id:
            query = query.where(TestRun.user_story_id == user_story_id)
        if task_id:
            query = query.where(TestRun.task_id == task_id)
        if subtask_id:
            query = query.where(TestRun.subtask_id == subtask_id)
        
        # Apply additional filters
        if status:
            query = query.where(TestRun.status == status)
        if run_type:
            query = query.where(TestRun.run_type == run_type)
        
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
        subtask_id: Optional[str] = None,
        status: Optional[str] = None,
        run_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestRun]:
        """
        Get test runs including all descendants in the hierarchy.
        """
        from app.models.hierarchy import Project, Usecase, UserStory, Task, Subtask
        from sqlalchemy import or_, and_
        
        query = select(TestRun).where(TestRun.is_deleted == False)
        
        # Build hierarchy conditions
        hierarchy_conditions = []
        
        if subtask_id:
            hierarchy_conditions.append(TestRun.subtask_id == subtask_id)
        elif task_id:
            hierarchy_conditions.append(TestRun.task_id == task_id)
            
            subtask_subquery = select(Subtask.id).where(
                and_(Subtask.task_id == task_id, Subtask.is_deleted == False)
            )
            subtask_result = await db.execute(subtask_subquery)
            subtask_ids = [row[0] for row in subtask_result.fetchall()]
            
            if subtask_ids:
                hierarchy_conditions.append(TestRun.subtask_id.in_(subtask_ids))
        elif user_story_id:
            hierarchy_conditions.append(TestRun.user_story_id == user_story_id)
            
            task_subquery = select(Task.id).where(
                and_(Task.user_story_id == user_story_id, Task.is_deleted == False)
            )
            task_result = await db.execute(task_subquery)
            task_ids = [row[0] for row in task_result.fetchall()]
            
            if task_ids:
                hierarchy_conditions.append(TestRun.task_id.in_(task_ids))
                
                subtask_subquery = select(Subtask.id).where(
                    and_(Subtask.task_id.in_(task_ids), Subtask.is_deleted == False)
                )
                subtask_result = await db.execute(subtask_subquery)
                subtask_ids = [row[0] for row in subtask_result.fetchall()]
                
                if subtask_ids:
                    hierarchy_conditions.append(TestRun.subtask_id.in_(subtask_ids))
        elif usecase_id:
            hierarchy_conditions.append(TestRun.usecase_id == usecase_id)
            
            user_story_subquery = select(UserStory.id).where(
                and_(UserStory.usecase_id == usecase_id, UserStory.is_deleted == False)
            )
            user_story_result = await db.execute(user_story_subquery)
            user_story_ids = [row[0] for row in user_story_result.fetchall()]
            
            if user_story_ids:
                hierarchy_conditions.append(TestRun.user_story_id.in_(user_story_ids))
                
                task_subquery = select(Task.id).where(
                    and_(Task.user_story_id.in_(user_story_ids), Task.is_deleted == False)
                )
                task_result = await db.execute(task_subquery)
                task_ids = [row[0] for row in task_result.fetchall()]
                
                if task_ids:
                    hierarchy_conditions.append(TestRun.task_id.in_(task_ids))
                    
                    subtask_subquery = select(Subtask.id).where(
                        and_(Subtask.task_id.in_(task_ids), Subtask.is_deleted == False)
                    )
                    subtask_result = await db.execute(subtask_subquery)
                    subtask_ids = [row[0] for row in subtask_result.fetchall()]
                    
                    if subtask_ids:
                        hierarchy_conditions.append(TestRun.subtask_id.in_(subtask_ids))
        elif project_id:
            hierarchy_conditions.append(TestRun.project_id == project_id)
            
            usecase_subquery = select(Usecase.id).where(
                and_(Usecase.project_id == project_id, Usecase.is_deleted == False)
            )
            usecase_result = await db.execute(usecase_subquery)
            usecase_ids = [row[0] for row in usecase_result.fetchall()]
            
            if usecase_ids:
                hierarchy_conditions.append(TestRun.usecase_id.in_(usecase_ids))
                
                user_story_subquery = select(UserStory.id).where(
                    and_(UserStory.usecase_id.in_(usecase_ids), UserStory.is_deleted == False)
                )
                user_story_result = await db.execute(user_story_subquery)
                user_story_ids = [row[0] for row in user_story_result.fetchall()]
                
                if user_story_ids:
                    hierarchy_conditions.append(TestRun.user_story_id.in_(user_story_ids))
                    
                    task_subquery = select(Task.id).where(
                        and_(Task.user_story_id.in_(user_story_ids), Task.is_deleted == False)
                    )
                    task_result = await db.execute(task_subquery)
                    task_ids = [row[0] for row in task_result.fetchall()]
                    
                    if task_ids:
                        hierarchy_conditions.append(TestRun.task_id.in_(task_ids))
                        
                        subtask_subquery = select(Subtask.id).where(
                            and_(Subtask.task_id.in_(task_ids), Subtask.is_deleted == False)
                        )
                        subtask_result = await db.execute(subtask_subquery)
                        subtask_ids = [row[0] for row in subtask_result.fetchall()]
                        
                        if subtask_ids:
                            hierarchy_conditions.append(TestRun.subtask_id.in_(subtask_ids))
        
        # Apply hierarchy conditions with OR
        if hierarchy_conditions:
            query = query.where(or_(*hierarchy_conditions))
        
        # Apply additional filters
        if status:
            query = query.where(TestRun.status == status)
        if run_type:
            query = query.where(TestRun.run_type == run_type)
        
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
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Validate that exactly one hierarchy level is set.
        """
        from app.models.hierarchy import Project, Usecase, UserStory, Task, Subtask
        from sqlalchemy import and_
        
        hierarchy_fields = [project_id, usecase_id, user_story_id, task_id, subtask_id]
        set_count = sum(1 for field in hierarchy_fields if field is not None)
        
        if set_count == 0:
            return False, "Exactly one hierarchy level must be set (project, usecase, user_story, task, or subtask)"
        elif set_count > 1:
            return False, "Only one hierarchy level can be set at a time"
        
        # Validate that the referenced entity exists
        if project_id:
            result = await db.execute(
                select(Project).where(and_(Project.id == project_id, Project.is_deleted == False))
            )
            if not result.scalar_one_or_none():
                return False, f"Project with id {project_id} not found"
        elif usecase_id:
            result = await db.execute(
                select(Usecase).where(and_(Usecase.id == usecase_id, Usecase.is_deleted == False))
            )
            if not result.scalar_one_or_none():
                return False, f"Use case with id {usecase_id} not found"
        elif user_story_id:
            result = await db.execute(
                select(UserStory).where(and_(UserStory.id == user_story_id, UserStory.is_deleted == False))
            )
            if not result.scalar_one_or_none():
                return False, f"User story with id {user_story_id} not found"
        elif task_id:
            result = await db.execute(
                select(Task).where(and_(Task.id == task_id, Task.is_deleted == False))
            )
            if not result.scalar_one_or_none():
                return False, f"Task with id {task_id} not found"
        elif subtask_id:
            result = await db.execute(
                select(Subtask).where(and_(Subtask.id == subtask_id, Subtask.is_deleted == False))
            )
            if not result.scalar_one_or_none():
                return False, f"Subtask with id {subtask_id} not found"
        
        return True, ""
    
    async def calculate_metrics(
        self,
        db: AsyncSession,
        *,
        test_run_id: str
    ) -> Dict[str, int]:
        """
        Calculate test run metrics (passed, failed, blocked counts).
        """
        from app.models.test_case import TestCase
        from sqlalchemy import and_
        
        # Get all test cases for this test run
        query = select(TestCase).where(
            and_(TestCase.test_run_id == test_run_id, TestCase.is_deleted == False)
        )
        result = await db.execute(query)
        test_cases = result.scalars().all()
        
        # Calculate metrics
        metrics = {
            "total": len(test_cases),
            "passed": sum(1 for tc in test_cases if tc.status == "Passed"),
            "failed": sum(1 for tc in test_cases if tc.status == "Failed"),
            "blocked": sum(1 for tc in test_cases if tc.status == "Blocked"),
            "skipped": sum(1 for tc in test_cases if tc.status == "Skipped"),
            "not_executed": sum(1 for tc in test_cases if tc.status == "Not Executed")
        }
        
        return metrics
    
    async def update_metrics(
        self,
        db: AsyncSession,
        *,
        test_run_id: str
    ) -> TestRun:
        """
        Update test run metrics based on current test case statuses.
        """
        # Get the test run
        test_run = await self.get(db, id=test_run_id)
        if not test_run:
            raise ValueError(f"Test run with id {test_run_id} not found")
        
        # Calculate metrics
        metrics = await self.calculate_metrics(db, test_run_id=test_run_id)
        
        # Update test run
        test_run.total_test_cases = metrics["total"]
        test_run.passed_test_cases = metrics["passed"]
        test_run.failed_test_cases = metrics["failed"]
        test_run.blocked_test_cases = metrics["blocked"]
        
        db.add(test_run)
        await db.commit()
        await db.refresh(test_run)
        
        return test_run


# Create instances
test_execution = CRUDTestExecution(TestExecution)
test_run = CRUDTestRun(TestRun)

"""
Test execution management endpoints for the Worky API.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.schemas.test_execution import (
    TestExecutionCreate,
    TestExecutionResponse,
    TestRunCreate,
    TestRunUpdate,
    TestRunResponse
)
from app.schemas.bug import BugCreate, BugResponse
from app.crud.crud_test_execution import test_execution, test_run
from app.crud.crud_test_case import test_case
from app.crud.crud_bug import bug
from app.core.security import get_current_user
from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException
)
from app.core.logging import StructuredLogger
from app.models.test_case import TestCaseBug

router = APIRouter()
logger = StructuredLogger(__name__)


@router.post("/", response_model=TestExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_test_execution(
    execution_data: TestExecutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a test case execution.
    
    Creates a new test execution record with:
    - Execution status (Passed, Failed, Blocked, Skipped, Not Applicable)
    - Actual results and notes
    - Environment details (browser, OS, device)
    - Optional attachments (screenshots, logs)
    
    Also updates the test case's last execution information.
    
    Requirements: 9.1, 9.2, 9.3
    """
    
    # Verify test case exists
    tc = await test_case.get(db, id=execution_data.test_case_id)
    if not tc or tc.is_deleted:
        raise ResourceNotFoundException("Test case", execution_data.test_case_id)
    
    # Verify test run exists if specified
    if execution_data.test_run_id:
        tr = await test_run.get(db, id=execution_data.test_run_id)
        if not tr or tr.is_deleted:
            raise ResourceNotFoundException("Test run", execution_data.test_run_id)
    
    # Set execution date if not provided
    if not execution_data.execution_date:
        execution_data.execution_date = datetime.utcnow()
    
    # Create execution record
    execution = await test_execution.create(
        db,
        obj_in=execution_data,
        executed_by=str(current_user.id)
    )
    
    # Update test run metrics if execution is part of a test run
    if execution_data.test_run_id:
        await test_run.update_metrics(db, test_run_id=execution_data.test_run_id)
    
    logger.log_activity(
        action="create_test_execution",
        entity_type="test_execution",
        entity_id=str(execution.id),
        test_case_id=execution_data.test_case_id,
        execution_status=execution_data.execution_status.value,
        test_run_id=execution_data.test_run_id
    )
    
    return TestExecutionResponse.from_orm(execution)


@router.get("/{execution_id}", response_model=TestExecutionResponse)
async def get_test_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific test execution by ID.
    
    Returns complete execution details including:
    - Execution status and results
    - Executor and execution date
    - Environment details
    - Attachments
    
    Requirements: 9.1, 9.2
    """
    
    execution = await test_execution.get(db, id=execution_id)
    
    if not execution:
        raise ResourceNotFoundException("Test execution", execution_id)
    
    logger.log_activity(
        action="view_test_execution",
        entity_type="test_execution",
        entity_id=execution_id
    )
    
    return TestExecutionResponse.from_orm(execution)


@router.post("/{execution_id}/create-bug", response_model=BugResponse, status_code=status.HTTP_201_CREATED)
async def create_bug_from_execution(
    execution_id: str,
    bug_data: BugCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a bug from a failed test execution.
    
    Pre-populates bug with test case details and links the bug to the test case.
    The bug inherits the hierarchy association from the test case.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.4
    """
    
    # Verify execution exists (TestExecution doesn't have is_deleted field)
    from sqlalchemy import select
    from app.models.test_execution import TestExecution
    result = await db.execute(
        select(TestExecution).where(TestExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise ResourceNotFoundException("Test execution", execution_id)
    
    # Verify test case exists
    tc = await test_case.get(db, id=execution.test_case_id)
    if not tc or tc.is_deleted:
        raise ResourceNotFoundException("Test case", execution.test_case_id)
    
    # Validate execution status (should be Failed, but allow other statuses too)
    if execution.execution_status not in ["Failed", "Blocked"]:
        logger.warning(
            f"Creating bug from execution with status '{execution.execution_status}'. "
            f"Typically bugs are created from Failed or Blocked executions."
        )
    
    # Inherit hierarchy from test case if not specified in bug_data
    if not any([
        bug_data.client_id, bug_data.program_id, bug_data.project_id,
        bug_data.usecase_id, bug_data.user_story_id, bug_data.task_id, bug_data.subtask_id
    ]):
        # Set hierarchy based on test case association
        if tc.project_id:
            bug_data.project_id = tc.project_id
        elif tc.usecase_id:
            bug_data.usecase_id = tc.usecase_id
        elif tc.user_story_id:
            bug_data.user_story_id = tc.user_story_id
        elif tc.task_id:
            bug_data.task_id = tc.task_id
    
    # Pre-populate bug fields from test case and execution if not provided
    if not bug_data.steps_to_reproduce and tc.test_steps:
        bug_data.steps_to_reproduce = tc.test_steps
    
    if not bug_data.expected_behavior and tc.expected_result:
        bug_data.expected_behavior = tc.expected_result
    
    if not bug_data.actual_behavior and execution.actual_result:
        bug_data.actual_behavior = execution.actual_result
    
    # Inherit environment details from execution
    if not bug_data.environment and execution.environment:
        bug_data.environment = execution.environment
    if not bug_data.browser and execution.browser:
        bug_data.browser = execution.browser
    if not bug_data.os and execution.os:
        bug_data.os = execution.os
    if not bug_data.device_type and execution.device_type:
        bug_data.device_type = execution.device_type
    
    # Create the bug
    created_bug = await bug.create(
        db,
        obj_in=bug_data,
        reported_by=str(current_user.id)
    )
    
    # Link bug to test case via test_case_bugs junction table
    test_case_bug_link = TestCaseBug(
        test_case_id=tc.id,
        bug_id=created_bug.id,
        test_execution_id=execution_id,
        created_by=str(current_user.id)
    )
    db.add(test_case_bug_link)
    await db.commit()
    
    logger.log_activity(
        action="create_bug_from_execution",
        entity_type="bug",
        entity_id=str(created_bug.id),
        test_case_id=tc.id,
        test_execution_id=execution_id,
        severity=created_bug.severity,
        priority=created_bug.priority
    )
    
    return BugResponse.from_orm(created_bug)


@router.post("/test-runs/", response_model=TestRunResponse, status_code=status.HTTP_201_CREATED)
async def create_test_run(
    test_run_data: TestRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new test run to group multiple test executions.
    
    Test runs are used to organize test executions for:
    - Sprint testing
    - Release testing
    - Regression testing
    
    Requirements: 9.8, 9.11
    """
    
    # Set start date if not provided
    if not test_run_data.start_date:
        test_run_data.start_date = datetime.utcnow()
    
    # Create test run
    tr = await test_run.create(
        db,
        obj_in=test_run_data,
        created_by=str(current_user.id)
    )
    
    logger.log_activity(
        action="create_test_run",
        entity_type="test_run",
        entity_id=str(tr.id),
        name=tr.name,
        sprint_id=tr.sprint_id
    )
    
    return TestRunResponse.from_orm(tr)


@router.get("/test-runs/{test_run_id}", response_model=TestRunResponse)
async def get_test_run(
    test_run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a test run with execution summary and metrics.
    
    Returns:
    - Test run details
    - Execution counts (total, passed, failed, blocked, skipped)
    - Pass rate and fail rate
    
    Requirements: 9.8, 9.11
    """
    
    # Get test run with updated metrics
    tr = await test_run.get_with_metrics(db, test_run_id=test_run_id)
    
    if not tr or tr.is_deleted:
        raise ResourceNotFoundException("Test run", test_run_id)
    
    # Calculate pass and fail rates
    response = TestRunResponse.from_orm(tr)
    if tr.total_tests > 0:
        response.pass_rate = round((tr.passed_tests / tr.total_tests) * 100, 2)
        response.fail_rate = round((tr.failed_tests / tr.total_tests) * 100, 2)
    else:
        response.pass_rate = 0.0
        response.fail_rate = 0.0
    
    logger.log_activity(
        action="view_test_run",
        entity_type="test_run",
        entity_id=test_run_id
    )
    
    return response


@router.put("/test-runs/{test_run_id}", response_model=TestRunResponse)
async def update_test_run(
    test_run_id: str,
    test_run_data: TestRunUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a test run.
    
    Can update:
    - Name and description
    - Status (In Progress, Completed, Aborted)
    - End date
    
    Metrics are automatically recalculated from executions.
    
    Requirements: 9.8, 9.11
    """
    
    tr = await test_run.get(db, id=test_run_id)
    
    if not tr or tr.is_deleted:
        raise ResourceNotFoundException("Test run", test_run_id)
    
    # Update test run
    updated_tr = await test_run.update(
        db,
        db_obj=tr,
        obj_in=test_run_data,
        updated_by=str(current_user.id)
    )
    
    # Recalculate metrics
    updated_tr = await test_run.update_metrics(db, test_run_id=test_run_id)
    
    # Calculate pass and fail rates
    response = TestRunResponse.from_orm(updated_tr)
    if updated_tr.total_tests > 0:
        response.pass_rate = round((updated_tr.passed_tests / updated_tr.total_tests) * 100, 2)
        response.fail_rate = round((updated_tr.failed_tests / updated_tr.total_tests) * 100, 2)
    else:
        response.pass_rate = 0.0
        response.fail_rate = 0.0
    
    logger.log_activity(
        action="update_test_run",
        entity_type="test_run",
        entity_id=test_run_id,
        changes=test_run_data.dict(exclude_unset=True)
    )
    
    return response

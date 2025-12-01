"""
Test run management endpoints for the Worky API.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.schemas.test_execution import (
    TestRunCreate,
    TestRunUpdate,
    TestRunResponse,
    TestRunList
)
from app.crud.crud_test_execution import test_run
from app.core.security import get_current_user
from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException
)
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=TestRunList)
async def list_test_runs(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    usecase_id: Optional[str] = Query(None, description="Filter by use case ID"),
    user_story_id: Optional[str] = Query(None, description="Filter by user story ID"),
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    subtask_id: Optional[str] = Query(None, description="Filter by subtask ID"),
    status: Optional[str] = Query(None, description="Filter by status (In Progress, Completed, Aborted)"),
    run_type: Optional[str] = Query(None, description="Filter by run type (Misc, One-Timer)"),
    include_descendants: bool = Query(False, description="Include test runs from descendant hierarchy levels"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of test runs with hierarchy filters.
    
    Test runs can be filtered by:
    - Hierarchy level (project, use case, user story, task, subtask)
    - Status (In Progress, Completed, Aborted)
    - Run type (Misc, One-Timer)
    
    When include_descendants is True, returns test runs from the selected
    hierarchy level and all its descendants.
    
    Returns test runs with metrics:
    - Total test cases
    - Passed, failed, blocked test case counts
    - Pass rate and completion percentage
    
    Requirements: 2.1, 2.5, 2.6, 2.7
    """
    
    # Get test runs based on hierarchy filter
    if include_descendants:
        test_runs = await test_run.get_with_descendants(
            db,
            project_id=project_id,
            usecase_id=usecase_id,
            user_story_id=user_story_id,
            task_id=task_id,
            subtask_id=subtask_id,
            status=status,
            run_type=run_type,
            skip=skip,
            limit=limit
        )
    else:
        test_runs = await test_run.get_by_hierarchy(
            db,
            project_id=project_id,
            usecase_id=usecase_id,
            user_story_id=user_story_id,
            task_id=task_id,
            subtask_id=subtask_id,
            status=status,
            run_type=run_type,
            skip=skip,
            limit=limit
        )
    
    # Calculate pass rate and completion percentage for each test run
    test_run_responses = []
    for tr in test_runs:
        response = TestRunResponse.from_orm(tr)
        
        # Calculate pass rate
        if tr.total_test_cases > 0:
            response.pass_rate = round((tr.passed_test_cases / tr.total_test_cases) * 100, 2)
            
            # Calculate completion percentage (non-"Not Executed" test cases)
            executed_count = tr.passed_test_cases + tr.failed_test_cases + tr.blocked_test_cases
            response.completion_percentage = round((executed_count / tr.total_test_cases) * 100, 2)
        else:
            response.pass_rate = 0.0
            response.completion_percentage = 0.0
        
        test_run_responses.append(response)
    
    # Get total count for pagination
    # For simplicity, we'll use the length of results as total
    # In production, you'd want a separate count query
    total = len(test_run_responses)
    
    logger.log_activity(
        action="list_test_runs",
        entity_type="test_run",
        filters={
            "project_id": project_id,
            "usecase_id": usecase_id,
            "user_story_id": user_story_id,
            "task_id": task_id,
            "subtask_id": subtask_id,
            "status": status,
            "run_type": run_type,
            "include_descendants": include_descendants
        },
        result_count=len(test_run_responses)
    )
    
    return TestRunList(
        test_runs=test_run_responses,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{test_run_id}", response_model=TestRunResponse)
async def get_test_run(
    test_run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific test run by ID.
    
    Returns complete test run details including:
    - Test run information (name, purpose, description)
    - Hierarchy association
    - Status and run type
    - Test case metrics (total, passed, failed, blocked)
    - Pass rate and completion percentage
    
    Requirements: 2.2
    """
    
    tr = await test_run.get(db, id=test_run_id)
    
    if not tr or tr.is_deleted:
        raise ResourceNotFoundException("Test run", test_run_id)
    
    # Update metrics to ensure they're current
    tr = await test_run.update_metrics(db, test_run_id=test_run_id)
    
    # Calculate pass rate and completion percentage
    response = TestRunResponse.from_orm(tr)
    if tr.total_test_cases > 0:
        response.pass_rate = round((tr.passed_test_cases / tr.total_test_cases) * 100, 2)
        
        executed_count = tr.passed_test_cases + tr.failed_test_cases + tr.blocked_test_cases
        response.completion_percentage = round((executed_count / tr.total_test_cases) * 100, 2)
    else:
        response.pass_rate = 0.0
        response.completion_percentage = 0.0
    
    logger.log_activity(
        action="view_test_run",
        entity_type="test_run",
        entity_id=test_run_id
    )
    
    return response


@router.post("/", response_model=TestRunResponse, status_code=status.HTTP_201_CREATED)
async def create_test_run(
    test_run_data: TestRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new test run.
    
    Test runs are containers for test cases and can be attached to any hierarchy level:
    - Project
    - Use Case
    - User Story
    - Task
    - Subtask
    
    Exactly one hierarchy level must be specified.
    
    Test run types:
    - Misc: General purpose test run
    - One-Timer: Single execution test run
    
    Requirements: 2.2, 2.3
    """
    
    # Validate hierarchy constraint
    is_valid, error_message = await test_run.validate_hierarchy_constraint(
        db,
        project_id=test_run_data.project_id,
        usecase_id=test_run_data.usecase_id,
        user_story_id=test_run_data.user_story_id,
        task_id=test_run_data.task_id,
        subtask_id=test_run_data.subtask_id
    )
    
    if not is_valid:
        raise ValidationException(error_message)
    
    # Set start date if not provided
    if not test_run_data.start_date:
        test_run_data.start_date = datetime.utcnow()
    
    # Create test run
    tr = await test_run.create(
        db,
        obj_in=test_run_data,
        created_by=str(current_user.id)
    )
    
    response = TestRunResponse.from_orm(tr)
    response.pass_rate = 0.0
    response.completion_percentage = 0.0
    
    logger.log_activity(
        action="create_test_run",
        entity_type="test_run",
        entity_id=str(tr.id),
        name=tr.name,
        run_type=tr.run_type,
        hierarchy={
            "project_id": tr.project_id,
            "usecase_id": tr.usecase_id,
            "user_story_id": tr.user_story_id,
            "task_id": tr.task_id,
            "subtask_id": tr.subtask_id
        }
    )
    
    return response


@router.put("/{test_run_id}", response_model=TestRunResponse)
async def update_test_run(
    test_run_id: str,
    test_run_data: TestRunUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a test run.
    
    Can update:
    - Name, purpose, descriptions
    - Component attached to
    - Run type
    - Status (In Progress, Completed, Aborted)
    - End date
    
    Metrics are automatically recalculated from test cases.
    
    Requirements: 2.3, 2.4
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
    
    # Calculate pass rate and completion percentage
    response = TestRunResponse.from_orm(updated_tr)
    if updated_tr.total_test_cases > 0:
        response.pass_rate = round((updated_tr.passed_test_cases / updated_tr.total_test_cases) * 100, 2)
        
        executed_count = updated_tr.passed_test_cases + updated_tr.failed_test_cases + updated_tr.blocked_test_cases
        response.completion_percentage = round((executed_count / updated_tr.total_test_cases) * 100, 2)
    else:
        response.pass_rate = 0.0
        response.completion_percentage = 0.0
    
    logger.log_activity(
        action="update_test_run",
        entity_type="test_run",
        entity_id=test_run_id,
        changes=test_run_data.dict(exclude_unset=True)
    )
    
    return response


@router.delete("/{test_run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_run(
    test_run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a test run.
    
    Sets the is_deleted flag to True. The test run and its test cases
    are not physically removed from the database.
    
    Requirements: 2.4
    """
    
    tr = await test_run.get(db, id=test_run_id)
    
    if not tr or tr.is_deleted:
        raise ResourceNotFoundException("Test run", test_run_id)
    
    # Soft delete
    await test_run.remove(db, id=test_run_id)
    
    logger.log_activity(
        action="delete_test_run",
        entity_type="test_run",
        entity_id=test_run_id
    )
    
    return None


@router.get("/{test_run_id}/metrics", response_model=dict)
async def get_test_run_metrics(
    test_run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed metrics for a test run.
    
    Returns:
    - Total test cases
    - Passed test cases count
    - Failed test cases count
    - Blocked test cases count
    - Skipped test cases count
    - Not executed test cases count
    - Pass rate (percentage)
    - Completion percentage (executed vs total)
    
    Requirements: 2.8, 11.6, 11.7, 13.10
    """
    
    tr = await test_run.get(db, id=test_run_id)
    
    if not tr or tr.is_deleted:
        raise ResourceNotFoundException("Test run", test_run_id)
    
    # Calculate current metrics
    metrics = await test_run.calculate_metrics(db, test_run_id=test_run_id)
    
    # Calculate rates
    total = metrics["total"]
    if total > 0:
        pass_rate = round((metrics["passed"] / total) * 100, 2)
        fail_rate = round((metrics["failed"] / total) * 100, 2)
        blocked_rate = round((metrics["blocked"] / total) * 100, 2)
        
        executed_count = metrics["passed"] + metrics["failed"] + metrics["blocked"] + metrics["skipped"]
        completion_percentage = round((executed_count / total) * 100, 2)
    else:
        pass_rate = 0.0
        fail_rate = 0.0
        blocked_rate = 0.0
        completion_percentage = 0.0
    
    result = {
        "test_run_id": test_run_id,
        "test_run_name": tr.name,
        "total_test_cases": metrics["total"],
        "passed_test_cases": metrics["passed"],
        "failed_test_cases": metrics["failed"],
        "blocked_test_cases": metrics["blocked"],
        "skipped_test_cases": metrics["skipped"],
        "not_executed_test_cases": metrics["not_executed"],
        "pass_rate": pass_rate,
        "fail_rate": fail_rate,
        "blocked_rate": blocked_rate,
        "completion_percentage": completion_percentage,
        "status": tr.status,
        "run_type": tr.run_type
    }
    
    logger.log_activity(
        action="view_test_run_metrics",
        entity_type="test_run",
        entity_id=test_run_id,
        metrics=result
    )
    
    return result

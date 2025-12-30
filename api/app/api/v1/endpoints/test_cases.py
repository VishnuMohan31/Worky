"""
Test case management endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.db.base import get_db
from app.models.user import User
from app.models.test_case import TestCase
from app.schemas.test_case import (
    TestCaseCreate, 
    TestCaseUpdate, 
    TestCaseResponse, 
    TestCaseList,
    TestCaseExecute
)
from app.schemas.bug import BugCreate, BugResponse
from app.crud.crud_test_case import test_case
from app.core.security import get_current_user, require_role
from app.core.exceptions import (
    ResourceNotFoundException, 
    AccessDeniedException, 
    ValidationException
)
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=TestCaseList)
async def list_test_cases(
    test_run_id: Optional[str] = Query(None, description="Filter by test run ID"),
    status: Optional[str] = Query(None, description="Filter by status (Not Executed, Passed, Failed, Blocked, Skipped)"),
    priority: Optional[str] = Query(None, description="Filter by priority (P0, P1, P2, P3)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List test cases with optional filters.
    
    Supports filtering by:
    - Test run ID (required or optional based on use case)
    - Status (Not Executed, Passed, Failed, Blocked, Skipped)
    - Priority (P0, P1, P2, P3)
    
    Returns test case list with execution info including:
    - Test case details
    - Execution status
    - Executor and execution timestamp
    """
    
    try:
        # Build query
        query = select(TestCase).where(TestCase.is_deleted == False)
        
        # Apply filters
        if test_run_id:
            query = query.where(TestCase.test_run_id == test_run_id)
        if status:
            query = query.where(TestCase.status == status)
        if priority:
            query = query.where(TestCase.priority == priority)
        
        # Count total
        count_query = select(func.count(TestCase.id)).where(TestCase.is_deleted == False)
        if test_run_id:
            count_query = count_query.where(TestCase.test_run_id == test_run_id)
        if status:
            count_query = count_query.where(TestCase.status == status)
        if priority:
            count_query = count_query.where(TestCase.priority == priority)
        
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()
        
        # Apply pagination and ordering
        query = query.order_by(TestCase.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        test_cases_list = result.scalars().all()
        
        # Build response with execution info
        test_case_responses = []
        for tc in test_cases_list:
            tc_response = TestCaseResponse.from_orm(tc)
            test_case_responses.append(tc_response)
        
        logger.log_activity(
            action="list_test_cases",
            entity_type="test_case",
            filters={
                "test_run_id": test_run_id,
                "status": status,
                "priority": priority
            },
            result_count=len(test_case_responses)
        )
        
        return TestCaseList(
            test_cases=test_case_responses,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing test cases: {str(e)}")
        raise


@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific test case by ID.
    
    Returns the complete test case details including:
    - All test case fields
    - Execution status and executor information
    """
    
    result = await db.execute(
        select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
    )
    tc = result.scalar_one_or_none()
    
    if not tc:
        raise ResourceNotFoundException("Test case", test_case_id)
    
    logger.log_activity(
        action="view_test_case",
        entity_type="test_case",
        entity_id=test_case_id
    )
    
    return TestCaseResponse.from_orm(tc)


@router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case_data: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new test case within a test run.
    
    Requirements:
    - test_run_id is required
    - test_case_name, test_case_steps, and expected_result are required
    - User must have Tester, Admin, or Project Manager role
    """
    
    # Verify test run exists
    from app.models.test_execution import TestRun
    test_run_result = await db.execute(
        select(TestRun).where(
            and_(
                TestRun.id == test_case_data.test_run_id,
                TestRun.is_deleted == False
            )
        )
    )
    test_run = test_run_result.scalar_one_or_none()
    
    if not test_run:
        raise ValidationException(f"Test run with id {test_case_data.test_run_id} not found")
    
    # Create test case
    tc_dict = test_case_data.dict()
    tc_dict["created_by"] = str(current_user.id)
    tc_dict["updated_by"] = str(current_user.id)
    
    tc = TestCase(**tc_dict)
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    
    # Update test run metrics
    from app.crud.crud_test_execution import test_run as crud_test_run
    await crud_test_run.update_metrics(db, test_run_id=test_case_data.test_run_id)
    
    logger.log_activity(
        action="create_test_case",
        entity_type="test_case",
        entity_id=str(tc.id),
        test_run_id=test_case_data.test_run_id,
        priority=tc.priority
    )
    
    return TestCaseResponse.from_orm(tc)


@router.put("/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: str,
    test_case_data: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a test case.
    
    Users can update test cases they created or if they have appropriate roles.
    """
    
    result = await db.execute(
        select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
    )
    tc = result.scalar_one_or_none()
    
    if not tc:
        raise ResourceNotFoundException("Test case", test_case_id)
    
    # Check permissions: creator, tester, or admin can update
    if current_user.role not in ["Admin", "Tester", "Project Manager"]:
        if tc.created_by != str(current_user.id):
            raise AccessDeniedException(
                "You can only update test cases you created"
            )
    
    # Update fields
    for field, value in test_case_data.dict(exclude_unset=True).items():
        setattr(tc, field, value)
    
    tc.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(tc)
    
    logger.log_activity(
        action="update_test_case",
        entity_type="test_case",
        entity_id=test_case_id,
        changes=test_case_data.dict(exclude_unset=True)
    )
    
    return TestCaseResponse.from_orm(tc)


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Tester", "Project Manager"]))
):
    """
    Soft delete a test case.
    
    Only users with Admin, Tester, or Project Manager roles can delete test cases.
    """
    
    result = await db.execute(
        select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
    )
    tc = result.scalar_one_or_none()
    
    if not tc:
        raise ResourceNotFoundException("Test case", test_case_id)
    
    # Soft delete
    tc.is_deleted = True
    tc.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_test_case",
        entity_type="test_case",
        entity_id=test_case_id
    )



@router.post("/{test_case_id}/execute", response_model=TestCaseResponse)
async def execute_test_case(
    test_case_id: str,
    execution_data: TestCaseExecute,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a test case and record results.
    
    Updates:
    - actual_result: The actual result from test execution
    - inference: Conclusion/analysis from execution
    - status: New status (Passed, Failed, Blocked, Skipped)
    - executed_by: Current user
    - executed_at: Current timestamp
    
    Also updates the test run metrics (passed, failed, blocked counts).
    """
    from datetime import datetime
    
    # Get test case
    result = await db.execute(
        select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
    )
    tc = result.scalar_one_or_none()
    
    if not tc:
        raise ResourceNotFoundException("Test case", test_case_id)
    
    # Update execution fields
    tc.actual_result = execution_data.actual_result
    tc.inference = execution_data.inference
    tc.status = execution_data.status.value
    tc.executed_by = str(current_user.id)
    tc.executed_at = datetime.utcnow()
    
    if execution_data.remarks:
        tc.remarks = execution_data.remarks
    
    tc.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(tc)
    
    # Update test run metrics
    if tc.test_run_id:
        from app.crud.crud_test_execution import test_run as crud_test_run
        await crud_test_run.update_metrics(db, test_run_id=tc.test_run_id)
    
    logger.log_activity(
        action="execute_test_case",
        entity_type="test_case",
        entity_id=test_case_id,
        status=execution_data.status.value,
        executed_by=str(current_user.id)
    )
    
    return TestCaseResponse.from_orm(tc)



@router.post("/{test_case_id}/create-bug", response_model=BugResponse, status_code=status.HTTP_201_CREATED)
async def create_bug_from_test_case(
    test_case_id: str,
    bug_data: Optional[BugCreate] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a bug from a failed test case.
    
    Pre-populates the bug with test case details:
    - Title: Copied from test case name
    - Reproduction steps: Copied from test case steps
    - Expected result: Copied from test case expected result
    - Actual result: Copied from test case actual result
    - Component: Copied from test case component_attached_to
    - Links bug to test case and test run
    
    The user can override any pre-populated fields by providing bug_data.
    """
    from app.models.bug import Bug
    
    # Get test case
    result = await db.execute(
        select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
    )
    tc = result.scalar_one_or_none()
    
    if not tc:
        raise ResourceNotFoundException("Test case", test_case_id)
    
    # Pre-populate bug data from test case
    bug_dict = {
        "title": tc.test_case_name,
        "description": tc.test_case_description or f"Bug found during test case execution: {tc.test_case_name}",
        "reproduction_steps": tc.test_case_steps,
        "expected_result": tc.expected_result,
        "actual_result": tc.actual_result or "",
        "component_attached_to": tc.component_attached_to,
        "test_run_id": tc.test_run_id,
        "test_case_id": tc.id,
        "reporter_id": str(current_user.id),
        "status": "New",
        "created_by": str(current_user.id),
        "updated_by": str(current_user.id)
    }
    
    # Override with user-provided data if available
    if bug_data:
        user_data = bug_data.dict(exclude_unset=True)
        bug_dict.update(user_data)
        # Ensure test_case_id and test_run_id are not overridden
        bug_dict["test_case_id"] = tc.id
        bug_dict["test_run_id"] = tc.test_run_id
    
    # Create bug
    bug = Bug(**bug_dict)
    db.add(bug)
    await db.commit()
    await db.refresh(bug)
    
    # Create link in test_case_bugs junction table
    from app.models.test_case import TestCaseBug
    test_case_bug = TestCaseBug(
        test_case_id=tc.id,
        bug_id=bug.id,
        created_by=str(current_user.id)
    )
    db.add(test_case_bug)
    await db.commit()
    
    logger.log_activity(
        action="create_bug_from_test_case",
        entity_type="bug",
        entity_id=str(bug.id),
        test_case_id=test_case_id,
        test_run_id=tc.test_run_id
    )
    
    # Send notification to assignee if assigned
    if bug.assignee_id:
        logger.log_activity(
            action="notify_bug_assignment",
            entity_type="bug",
            entity_id=str(bug.id),
            assignee_id=bug.assignee_id,
            message=f"Bug {bug.id} created from test case {test_case_id} and assigned to user {bug.assignee_id}"
        )
    
    return BugResponse.from_orm(bug)

"""
QA Metrics endpoints for bug and test execution analytics.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from datetime import datetime, timedelta

from app.db.base import get_db
from app.models.bug import Bug
from app.models.test_case import TestCase
from app.models.test_execution import TestExecution
from app.models.user import User
from app.core.security import get_current_user
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/bugs/summary")
async def get_bug_summary(
    client_id: Optional[str] = Query(None),
    program_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    usecase_id: Optional[str] = Query(None),
    user_story_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    subtask_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bug summary metrics including total, open, closed bugs,
    resolution rate, average resolution time, and distribution by
    severity, priority, and status.
    
    Supports hierarchy filtering to scope metrics to specific
    project areas.
    """
    
    try:
        # Build base query with hierarchy filters
        query = select(Bug).where(Bug.is_deleted == False)
        
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
        
        # Get all bugs matching filters
        result = await db.execute(query)
        bugs = result.scalars().all()
        
        total_bugs = len(bugs)
        
        # Count open and closed bugs
        open_statuses = ['New', 'Open', 'In Progress', 'Reopened']
        closed_statuses = ['Closed', 'Verified', 'Rejected']
        
        open_bugs = sum(1 for bug in bugs if bug.status in open_statuses)
        closed_bugs = sum(1 for bug in bugs if bug.status in closed_statuses)
        
        # Calculate resolution rate
        resolution_rate = (closed_bugs / total_bugs * 100) if total_bugs > 0 else 0
        
        # Calculate average resolution time (for closed bugs)
        resolution_times = []
        for bug in bugs:
            if bug.closed_at and bug.created_at:
                delta = bug.closed_at - bug.created_at
                resolution_times.append(delta.total_seconds() / 86400)  # Convert to days
        
        average_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Distribution by severity
        by_severity = {}
        for bug in bugs:
            severity = bug.severity or 'Unknown'
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Distribution by priority
        by_priority = {}
        for bug in bugs:
            priority = bug.priority or 'Unknown'
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        # Distribution by status
        by_status = {}
        for bug in bugs:
            status = bug.status or 'Unknown'
            by_status[status] = by_status.get(status, 0) + 1
        
        logger.log_activity(
            action="get_bug_summary_metrics",
            entity_type="metrics",
            total_bugs=total_bugs
        )
        
        return {
            "total_bugs": total_bugs,
            "open_bugs": open_bugs,
            "closed_bugs": closed_bugs,
            "resolution_rate": round(resolution_rate, 2),
            "average_resolution_time": round(average_resolution_time, 2),
            "by_severity": by_severity,
            "by_priority": by_priority,
            "by_status": by_status
        }
        
    except Exception as e:
        logger.error(f"Error getting bug summary metrics: {str(e)}")
        # Return empty metrics on error
        return {
            "total_bugs": 0,
            "open_bugs": 0,
            "closed_bugs": 0,
            "resolution_rate": 0,
            "average_resolution_time": 0,
            "by_severity": {},
            "by_priority": {},
            "by_status": {}
        }


@router.get("/bugs/trends")
async def get_bug_trends(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    client_id: Optional[str] = Query(None),
    program_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    usecase_id: Optional[str] = Query(None),
    user_story_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    subtask_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bug trend analysis showing bug creation and resolution rates over time.
    
    Returns data suitable for line charts showing trends in bug activity.
    Supports date range filtering and hierarchy filtering.
    """
    
    try:
        # Default to last 30 days if no date range specified
        if not end_date:
            end_date_obj = datetime.utcnow()
        else:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if not start_date:
            start_date_obj = end_date_obj - timedelta(days=30)
        else:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Build base query with hierarchy filters
        query = select(Bug).where(Bug.is_deleted == False)
        
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
        
        # Get all bugs
        result = await db.execute(query)
        bugs = result.scalars().all()
        
        # Generate date range
        dates = []
        created_counts = []
        resolved_counts = []
        
        current_date = start_date_obj
        while current_date <= end_date_obj:
            date_str = current_date.strftime("%Y-%m-%d")
            dates.append(date_str)
            
            # Count bugs created on this date
            created_count = sum(
                1 for bug in bugs
                if bug.created_at and bug.created_at.date() == current_date.date()
            )
            created_counts.append(created_count)
            
            # Count bugs resolved on this date
            resolved_count = sum(
                1 for bug in bugs
                if bug.closed_at and bug.closed_at.date() == current_date.date()
            )
            resolved_counts.append(resolved_count)
            
            current_date += timedelta(days=1)
        
        logger.log_activity(
            action="get_bug_trends",
            entity_type="metrics",
            date_range=f"{start_date} to {end_date}"
        )
        
        return {
            "dates": dates,
            "created": created_counts,
            "resolved": resolved_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting bug trends: {str(e)}")
        return {
            "dates": [],
            "created": [],
            "resolved": []
        }


@router.get("/bugs/aging")
async def get_bug_aging_report(
    client_id: Optional[str] = Query(None),
    program_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    usecase_id: Optional[str] = Query(None),
    user_story_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    subtask_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bug aging report showing bugs grouped by age ranges
    and average age by severity.
    
    Age ranges: 0-7 days, 8-30 days, 31-90 days, 90+ days
    """
    
    try:
        # Build base query with hierarchy filters
        query = select(Bug).where(
            and_(
                Bug.is_deleted == False,
                Bug.status.in_(['New', 'Open', 'In Progress', 'Reopened'])  # Only open bugs
            )
        )
        
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
        
        # Get all open bugs
        result = await db.execute(query)
        bugs = result.scalars().all()
        
        now = datetime.utcnow()
        
        # Calculate age for each bug
        bug_ages = []
        for bug in bugs:
            if bug.created_at:
                age_days = (now - bug.created_at).total_seconds() / 86400
                bug_ages.append({
                    'age': age_days,
                    'severity': bug.severity or 'Unknown'
                })
        
        # Group by age ranges
        age_ranges = [
            {'range': '0-7 days', 'min': 0, 'max': 7, 'count': 0},
            {'range': '8-30 days', 'min': 8, 'max': 30, 'count': 0},
            {'range': '31-90 days', 'min': 31, 'max': 90, 'count': 0},
            {'range': '90+ days', 'min': 91, 'max': float('inf'), 'count': 0}
        ]
        
        for bug_age in bug_ages:
            age = bug_age['age']
            for age_range in age_ranges:
                if age_range['min'] <= age <= age_range['max']:
                    age_range['count'] += 1
                    break
        
        # Calculate percentages
        total = len(bug_ages)
        for age_range in age_ranges:
            age_range['percentage'] = round((age_range['count'] / total * 100), 1) if total > 0 else 0
        
        # Calculate average age by severity
        severity_ages = {}
        severity_counts = {}
        
        for bug_age in bug_ages:
            severity = bug_age['severity']
            if severity not in severity_ages:
                severity_ages[severity] = 0
                severity_counts[severity] = 0
            severity_ages[severity] += bug_age['age']
            severity_counts[severity] += 1
        
        average_age_by_severity = {
            severity: round(severity_ages[severity] / severity_counts[severity], 1)
            for severity in severity_ages
        }
        
        logger.log_activity(
            action="get_bug_aging_report",
            entity_type="metrics",
            total_open_bugs=total
        )
        
        return {
            "age_ranges": [
                {
                    'range': ar['range'],
                    'count': ar['count'],
                    'percentage': ar['percentage']
                }
                for ar in age_ranges
            ],
            "average_age_by_severity": average_age_by_severity
        }
        
    except Exception as e:
        logger.error(f"Error getting bug aging report: {str(e)}")
        return {
            "age_ranges": [],
            "average_age_by_severity": {}
        }


@router.get("/test-execution/summary")
async def get_test_execution_summary(
    test_run_id: Optional[str] = Query(None, description="Filter by specific test run"),
    project_id: Optional[str] = Query(None),
    usecase_id: Optional[str] = Query(None),
    user_story_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get test execution metrics including pass rate, fail rate,
    and execution coverage.
    
    Can be filtered by test run or hierarchy level.
    """
    
    try:
        # Build query for test executions
        query = select(TestExecution)
        
        if test_run_id:
            query = query.where(TestExecution.test_run_id == test_run_id)
        
        # If hierarchy filters provided, join with test cases
        if any([project_id, usecase_id, user_story_id, task_id]):
            query = query.join(TestCase, TestExecution.test_case_id == TestCase.id)
            
            if project_id:
                query = query.where(TestCase.project_id == project_id)
            if usecase_id:
                query = query.where(TestCase.usecase_id == usecase_id)
            if user_story_id:
                query = query.where(TestCase.user_story_id == user_story_id)
            if task_id:
                query = query.where(TestCase.task_id == task_id)
        
        # Get all executions
        result = await db.execute(query)
        executions = result.scalars().all()
        
        total_executions = len(executions)
        
        # Count by status
        passed = sum(1 for ex in executions if ex.execution_status == 'Passed')
        failed = sum(1 for ex in executions if ex.execution_status == 'Failed')
        blocked = sum(1 for ex in executions if ex.execution_status == 'Blocked')
        skipped = sum(1 for ex in executions if ex.execution_status == 'Skipped')
        
        # Calculate rates
        pass_rate = (passed / total_executions * 100) if total_executions > 0 else 0
        fail_rate = (failed / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate execution coverage (percentage of test cases that have been executed)
        # Get total test cases in scope
        test_case_query = select(TestCase).where(TestCase.is_deleted == False)
        
        if project_id:
            test_case_query = test_case_query.where(TestCase.project_id == project_id)
        if usecase_id:
            test_case_query = test_case_query.where(TestCase.usecase_id == usecase_id)
        if user_story_id:
            test_case_query = test_case_query.where(TestCase.user_story_id == user_story_id)
        if task_id:
            test_case_query = test_case_query.where(TestCase.task_id == task_id)
        
        test_case_result = await db.execute(test_case_query)
        total_test_cases = len(test_case_result.scalars().all())
        
        # Get unique test cases that have been executed
        executed_test_case_ids = set(ex.test_case_id for ex in executions)
        executed_test_cases = len(executed_test_case_ids)
        
        execution_coverage = (executed_test_cases / total_test_cases * 100) if total_test_cases > 0 else 0
        
        logger.log_activity(
            action="get_test_execution_summary",
            entity_type="metrics",
            total_executions=total_executions
        )
        
        return {
            "total_executions": total_executions,
            "passed": passed,
            "failed": failed,
            "blocked": blocked,
            "skipped": skipped,
            "pass_rate": round(pass_rate, 2),
            "fail_rate": round(fail_rate, 2),
            "execution_coverage": round(execution_coverage, 2),
            "total_test_cases": total_test_cases,
            "executed_test_cases": executed_test_cases
        }
        
    except Exception as e:
        logger.error(f"Error getting test execution summary: {str(e)}")
        return {
            "total_executions": 0,
            "passed": 0,
            "failed": 0,
            "blocked": 0,
            "skipped": 0,
            "pass_rate": 0,
            "fail_rate": 0,
            "execution_coverage": 0,
            "total_test_cases": 0,
            "executed_test_cases": 0
        }

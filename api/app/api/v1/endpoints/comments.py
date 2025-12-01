"""
Comment management endpoints for bugs and test cases in the Worky API.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    BugCommentResponse,
    TestCaseCommentResponse,
    CommentList
)
from app.crud.crud_comment import comment as crud_comment
from app.services.notification_service import notification_service
from app.core.security import get_current_user
from app.core.exceptions import (
    ResourceNotFoundException,
    AccessDeniedException,
    ValidationException
)
from app.core.logging import StructuredLogger
import json

router = APIRouter()
logger = StructuredLogger(__name__)


# ============================================================================
# Bug Comment Endpoints
# ============================================================================

@router.get("/bugs/{bug_id}/comments", response_model=List[BugCommentResponse])
async def get_bug_comments(
    bug_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments for a specific bug.
    
    Returns comments in chronological order (oldest to newest).
    Includes comment text, author information, edit status, and attachments.
    """
    from app.models.bug import Bug
    from sqlalchemy import select, and_
    
    # Verify bug exists
    result = await db.execute(
        select(Bug).where(
            and_(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
    )
    bug = result.scalar_one_or_none()
    
    if not bug:
        raise ResourceNotFoundException("Bug", bug_id)
    
    # Get comments
    comments = await crud_comment.get_by_entity(
        db,
        entity_type="bug",
        entity_id=bug_id,
        skip=skip,
        limit=limit
    )
    
    # Build response with author names
    comment_responses = []
    for comment in comments:
        # Get author details
        author_result = await db.execute(
            select(User).where(User.id == comment.author_id)
        )
        author = author_result.scalar_one_or_none()
        author_name = author.username if author else "Unknown User"
        
        comment_response = BugCommentResponse(
            id=comment.id,
            bug_id=comment.bug_id,
            comment_text=comment.comment_text,
            author_id=comment.author_id,
            author_name=author_name,
            mentioned_users=comment.mentioned_users,
            attachments=comment.attachments,
            is_edited=comment.is_edited,
            edited_at=comment.edited_at,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            is_deleted=comment.is_deleted
        )
        comment_responses.append(comment_response)
    
    logger.log_activity(
        action="list_bug_comments",
        entity_type="bug",
        entity_id=bug_id,
        comment_count=len(comment_responses)
    )
    
    return comment_responses


@router.post("/bugs/{bug_id}/comments", response_model=BugCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_bug_comment(
    bug_id: str,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on a bug.
    
    Supports:
    - Rich text formatting
    - @mentions (automatically extracted from comment text)
    - File attachments
    
    Notifications are sent to:
    - Mentioned users
    - Bug assignee
    - Bug reporter
    """
    from app.models.bug import Bug
    from sqlalchemy import select, and_
    
    # Verify bug exists
    result = await db.execute(
        select(Bug).where(
            and_(
                Bug.id == bug_id,
                Bug.is_deleted == False
            )
        )
    )
    bug = result.scalar_one_or_none()
    
    if not bug:
        raise ResourceNotFoundException("Bug", bug_id)
    
    # Create comment
    comment = await crud_comment.create(
        db,
        entity_type="bug",
        entity_id=bug_id,
        comment_in=comment_data,
        author_id=str(current_user.id)
    )
    
    # Get author details for response
    author_result = await db.execute(
        select(User).where(User.id == comment.author_id)
    )
    author = author_result.scalar_one_or_none()
    author_name = author.username if author else "Unknown User"
    
    logger.log_activity(
        action="create_bug_comment",
        entity_type="bug",
        entity_id=bug_id,
        comment_id=comment.id,
        author_id=str(current_user.id)
    )
    
    # Send notifications to mentioned users
    if comment.mentioned_users:
        try:
            mentioned_user_ids = json.loads(comment.mentioned_users)
            # Resolve mentions to user IDs
            resolved_user_ids = await notification_service.resolve_mentions_to_user_ids(
                db, mentioned_user_ids
            )
            # Send notifications
            await notification_service.notify_mentioned_users(
                db,
                mentioned_user_ids=resolved_user_ids,
                entity_type="bug",
                entity_id=bug_id,
                comment_id=comment.id,
                author_id=str(current_user.id),
                comment_text=comment.comment_text
            )
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse mentioned_users JSON: {comment.mentioned_users}")
    
    # Send notifications to bug assignee and reporter
    await notification_service.notify_bug_comment_stakeholders(
        db,
        bug_id=bug_id,
        comment_id=comment.id,
        author_id=str(current_user.id),
        assignee_id=bug.assigned_to,
        reporter_id=bug.reported_by
    )
    
    return BugCommentResponse(
        id=comment.id,
        bug_id=comment.bug_id,
        comment_text=comment.comment_text,
        author_id=comment.author_id,
        author_name=author_name,
        mentioned_users=comment.mentioned_users,
        attachments=comment.attachments,
        is_edited=comment.is_edited,
        edited_at=comment.edited_at,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_deleted=comment.is_deleted
    )


# ============================================================================
# Test Case Comment Endpoints
# ============================================================================

@router.get("/test-cases/{test_case_id}/comments", response_model=List[TestCaseCommentResponse])
async def get_test_case_comments(
    test_case_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments for a specific test case.
    
    Returns comments in chronological order (oldest to newest).
    Includes comment text, author information, edit status, and attachments.
    """
    from app.models.test_case import TestCase
    from sqlalchemy import select, and_
    
    # Verify test case exists
    result = await db.execute(
        select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
    )
    test_case = result.scalar_one_or_none()
    
    if not test_case:
        raise ResourceNotFoundException("TestCase", test_case_id)
    
    # Get comments
    comments = await crud_comment.get_by_entity(
        db,
        entity_type="test_case",
        entity_id=test_case_id,
        skip=skip,
        limit=limit
    )
    
    # Build response with author names
    comment_responses = []
    for comment in comments:
        # Get author details
        author_result = await db.execute(
            select(User).where(User.id == comment.author_id)
        )
        author = author_result.scalar_one_or_none()
        author_name = author.username if author else "Unknown User"
        
        comment_response = TestCaseCommentResponse(
            id=comment.id,
            test_case_id=comment.test_case_id,
            comment_text=comment.comment_text,
            author_id=comment.author_id,
            author_name=author_name,
            mentioned_users=comment.mentioned_users,
            attachments=comment.attachments,
            is_edited=comment.is_edited,
            edited_at=comment.edited_at,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            is_deleted=comment.is_deleted
        )
        comment_responses.append(comment_response)
    
    logger.log_activity(
        action="list_test_case_comments",
        entity_type="test_case",
        entity_id=test_case_id,
        comment_count=len(comment_responses)
    )
    
    return comment_responses


@router.post("/test-cases/{test_case_id}/comments", response_model=TestCaseCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case_comment(
    test_case_id: str,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on a test case.
    
    Supports:
    - Rich text formatting
    - @mentions (automatically extracted from comment text)
    - File attachments
    
    Notifications are sent to mentioned users.
    """
    from app.models.test_case import TestCase
    from sqlalchemy import select, and_
    
    # Verify test case exists
    result = await db.execute(
        select(TestCase).where(
            and_(
                TestCase.id == test_case_id,
                TestCase.is_deleted == False
            )
        )
    )
    test_case = result.scalar_one_or_none()
    
    if not test_case:
        raise ResourceNotFoundException("TestCase", test_case_id)
    
    # Create comment
    comment = await crud_comment.create(
        db,
        entity_type="test_case",
        entity_id=test_case_id,
        comment_in=comment_data,
        author_id=str(current_user.id)
    )
    
    # Get author details for response
    author_result = await db.execute(
        select(User).where(User.id == comment.author_id)
    )
    author = author_result.scalar_one_or_none()
    author_name = author.username if author else "Unknown User"
    
    logger.log_activity(
        action="create_test_case_comment",
        entity_type="test_case",
        entity_id=test_case_id,
        comment_id=comment.id,
        author_id=str(current_user.id)
    )
    
    # Send notifications to mentioned users
    if comment.mentioned_users:
        try:
            mentioned_user_ids = json.loads(comment.mentioned_users)
            # Resolve mentions to user IDs
            resolved_user_ids = await notification_service.resolve_mentions_to_user_ids(
                db, mentioned_user_ids
            )
            # Send notifications
            await notification_service.notify_mentioned_users(
                db,
                mentioned_user_ids=resolved_user_ids,
                entity_type="test_case",
                entity_id=test_case_id,
                comment_id=comment.id,
                author_id=str(current_user.id),
                comment_text=comment.comment_text
            )
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse mentioned_users JSON: {comment.mentioned_users}")
    
    return TestCaseCommentResponse(
        id=comment.id,
        test_case_id=comment.test_case_id,
        comment_text=comment.comment_text,
        author_id=comment.author_id,
        author_name=author_name,
        mentioned_users=comment.mentioned_users,
        attachments=comment.attachments,
        is_edited=comment.is_edited,
        edited_at=comment.edited_at,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_deleted=comment.is_deleted
    )


# ============================================================================
# Generic Comment Endpoints (for both bugs and test cases)
# ============================================================================

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    entity_type: str = Query(..., description="Type of entity: 'bug' or 'test_case'"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment.
    
    Restrictions:
    - Only the comment author can edit their own comments
    - Comments can only be edited within 15 minutes of posting
    - Edited comments are marked with an "edited" indicator and timestamp
    
    When comment text is updated, @mentions are automatically re-extracted.
    """
    
    # Validate entity_type
    if entity_type not in ["bug", "test_case"]:
        raise ValidationException("entity_type must be 'bug' or 'test_case'")
    
    # Update comment with validation
    updated_comment, error_msg = await crud_comment.update(
        db,
        comment_id=comment_id,
        entity_type=entity_type,
        comment_in=comment_data,
        user_id=str(current_user.id)
    )
    
    if error_msg:
        if "not found" in error_msg:
            raise ResourceNotFoundException("Comment", comment_id)
        elif "Only the comment author" in error_msg:
            raise AccessDeniedException(error_msg)
        elif "can only be edited within" in error_msg:
            raise ValidationException(error_msg)
        else:
            raise ValidationException(error_msg)
    
    if not updated_comment:
        raise ResourceNotFoundException("Comment", comment_id)
    
    # Get author details for response
    from sqlalchemy import select
    author_result = await db.execute(
        select(User).where(User.id == updated_comment.author_id)
    )
    author = author_result.scalar_one_or_none()
    author_name = author.username if author else "Unknown User"
    
    logger.log_activity(
        action="update_comment",
        entity_type=entity_type,
        comment_id=comment_id,
        author_id=str(current_user.id)
    )
    
    return CommentResponse(
        id=updated_comment.id,
        comment_text=updated_comment.comment_text,
        author_id=updated_comment.author_id,
        author_name=author_name,
        mentioned_users=updated_comment.mentioned_users,
        attachments=updated_comment.attachments,
        is_edited=updated_comment.is_edited,
        edited_at=updated_comment.edited_at,
        created_at=updated_comment.created_at,
        updated_at=updated_comment.updated_at,
        is_deleted=updated_comment.is_deleted
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    entity_type: str = Query(..., description="Type of entity: 'bug' or 'test_case'"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment (soft delete).
    
    Restrictions:
    - Only the comment author can delete their own comments
    
    The comment is soft-deleted (marked as deleted but not removed from database).
    """
    
    # Validate entity_type
    if entity_type not in ["bug", "test_case"]:
        raise ValidationException("entity_type must be 'bug' or 'test_case'")
    
    # Delete comment with validation
    success, error_msg = await crud_comment.delete(
        db,
        comment_id=comment_id,
        entity_type=entity_type,
        user_id=str(current_user.id)
    )
    
    if not success:
        if "not found" in error_msg:
            raise ResourceNotFoundException("Comment", comment_id)
        elif "Only the comment author" in error_msg:
            raise AccessDeniedException(error_msg)
        else:
            raise ValidationException(error_msg)
    
    logger.log_activity(
        action="delete_comment",
        entity_type=entity_type,
        comment_id=comment_id,
        author_id=str(current_user.id)
    )

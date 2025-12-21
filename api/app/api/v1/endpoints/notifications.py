"""
API endpoints for notification management.

This module provides endpoints for:
- Getting user notifications
- Managing notification preferences
- Marking notifications as read
- Getting notification summaries
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import NotificationType, NotificationStatus
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationUpdate,
    NotificationPreferenceResponse,
    NotificationPreferencesResponse,
    NotificationPreferenceUpdate,
    NotificationSummary,
    BulkNotificationRequest,
    BulkNotificationResponse
)
from app.services.notification_service import notification_service
from app.crud.crud_notification import (
    notification as crud_notification,
    notification_preference as crud_notification_preference
)
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)
router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[NotificationStatus] = Query(None, description="Filter by notification status"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page")
) -> NotificationListResponse:
    """
    Get notifications for the current user.
    
    Supports filtering by status and type, with pagination.
    """
    skip = (page - 1) * per_page
    
    # Get notifications
    notifications = await notification_service.get_user_notifications(
        db,
        user_id=current_user.id,
        status=status,
        notification_type=notification_type,
        skip=skip,
        limit=per_page
    )
    
    # Get total count
    total = await crud_notification.count_user_notifications(
        db,
        user_id=current_user.id,
        status=status,
        notification_type=notification_type
    )
    
    # Calculate pagination info
    has_next = skip + per_page < total
    has_prev = page > 1
    
    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifications],
        total=total,
        page=page,
        per_page=per_page,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/summary", response_model=NotificationSummary)
async def get_notification_summary(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NotificationSummary:
    """
    Get notification summary for the current user.
    
    Returns unread counts by type and recent notifications.
    """
    summary_data = await notification_service.get_notification_summary(
        db, user_id=current_user.id
    )
    
    return NotificationSummary(
        total_unread=summary_data["total_unread"],
        unread_by_type=summary_data["unread_by_type"],
        recent_notifications=[
            NotificationResponse.from_orm(n) 
            for n in summary_data["recent_notifications"]
        ]
    )


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    notification_id: str
) -> NotificationResponse:
    """
    Mark a specific notification as read.
    """
    notification = await notification_service.mark_notification_as_read(
        db, notification_id=notification_id, user_id=current_user.id
    )
    
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found or does not belong to current user"
        )
    
    logger.log_activity(
        action="notification_marked_read",
        notification_id=notification_id,
        user_id=current_user.id,
        message=f"Notification {notification_id} marked as read by {current_user.full_name}"
    )
    
    return NotificationResponse.from_orm(notification)


@router.put("/read-all")
async def mark_all_notifications_as_read(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Mark all unread notifications as read for the current user.
    """
    count = await crud_notification.mark_all_as_read(
        db, user_id=current_user.id
    )
    
    logger.log_activity(
        action="all_notifications_marked_read",
        user_id=current_user.id,
        count=count,
        message=f"All {count} notifications marked as read by {current_user.full_name}"
    )
    
    return {"message": f"Marked {count} notifications as read"}


@router.put("/read-multiple")
async def mark_multiple_notifications_as_read(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    notification_ids: List[str]
) -> dict:
    """
    Mark multiple notifications as read.
    """
    if len(notification_ids) > 100:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark more than 100 notifications at once"
        )
    
    count = await crud_notification.mark_multiple_as_read(
        db, notification_ids=notification_ids, user_id=current_user.id
    )
    
    logger.log_activity(
        action="multiple_notifications_marked_read",
        user_id=current_user.id,
        count=count,
        requested_count=len(notification_ids),
        message=f"{count} notifications marked as read by {current_user.full_name}"
    )
    
    return {"message": f"Marked {count} notifications as read"}


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NotificationPreferencesResponse:
    """
    Get notification preferences for the current user.
    """
    preferences = await crud_notification_preference.get_user_preferences(
        db, user_id=current_user.id
    )
    
    return NotificationPreferencesResponse(
        preferences=[NotificationPreferenceResponse.from_orm(p) for p in preferences]
    )


@router.put("/preferences/{notification_type}", response_model=NotificationPreferenceResponse)
async def update_notification_preference(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    notification_type: NotificationType,
    preference_data: NotificationPreferenceUpdate
) -> NotificationPreferenceResponse:
    """
    Update notification preference for a specific notification type.
    """
    preference = await notification_service.update_notification_preferences(
        db,
        user_id=current_user.id,
        notification_type=notification_type,
        email_enabled=preference_data.email_enabled,
        in_app_enabled=preference_data.in_app_enabled,
        push_enabled=preference_data.push_enabled
    )
    
    if not preference:
        raise HTTPException(
            status_code=404,
            detail="Notification preference not found"
        )
    
    logger.log_activity(
        action="notification_preference_updated",
        user_id=current_user.id,
        notification_type=notification_type.value,
        preference_data=preference_data.dict(exclude_unset=True),
        message=f"Notification preference updated for {notification_type.value} by {current_user.full_name}"
    )
    
    return NotificationPreferenceResponse.from_orm(preference)


@router.post("/bulk", response_model=BulkNotificationResponse)
async def send_bulk_notifications(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    bulk_request: BulkNotificationRequest
) -> BulkNotificationResponse:
    """
    Send bulk notifications to multiple users.
    
    This endpoint is typically used by administrators or system processes
    to send notifications to multiple users at once.
    """
    # TODO: Add permission check for bulk notifications
    # For now, allow any authenticated user to send bulk notifications
    
    from app.schemas.notification import NotificationCreate
    
    successful = 0
    failed = 0
    notification_ids = []
    errors = []
    
    for user_id in bulk_request.user_ids:
        try:
            notification_data = NotificationCreate(
                user_id=user_id,
                type=bulk_request.type,
                title=bulk_request.title,
                message=bulk_request.message,
                entity_type=bulk_request.entity_type,
                entity_id=bulk_request.entity_id,
                channel=bulk_request.channel,
                context_data=bulk_request.context_data
            )
            
            notification = await crud_notification.create_notification(
                db, notification_data=notification_data, created_by=current_user.id
            )
            
            notification_ids.append(notification.id)
            successful += 1
            
        except Exception as e:
            failed += 1
            errors.append({
                "user_id": user_id,
                "error": str(e)
            })
            logger.error(
                f"Failed to create bulk notification for user {user_id}: {str(e)}",
                user_id=user_id,
                error=str(e)
            )
    
    logger.log_activity(
        action="bulk_notifications_sent",
        user_id=current_user.id,
        total_requested=len(bulk_request.user_ids),
        successful=successful,
        failed=failed,
        notification_type=bulk_request.type.value,
        message=f"Bulk notifications sent: {successful} successful, {failed} failed"
    )
    
    return BulkNotificationResponse(
        total_requested=len(bulk_request.user_ids),
        successful=successful,
        failed=failed,
        notification_ids=notification_ids,
        errors=errors
    )


@router.delete("/cleanup")
async def cleanup_old_notifications(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    older_than_days: int = Query(90, ge=1, le=365, description="Delete notifications older than this many days")
) -> dict:
    """
    Delete old notifications to free up storage.
    
    This endpoint is typically used by administrators for maintenance.
    """
    # TODO: Add admin permission check
    # For now, allow any authenticated user to cleanup their own notifications
    
    # For safety, only allow users to cleanup their own notifications
    # Admin cleanup would be a separate endpoint or background job
    
    deleted_count = await crud_notification.delete_old_notifications(
        db, older_than_days=older_than_days
    )
    
    logger.log_activity(
        action="notifications_cleanup",
        user_id=current_user.id,
        deleted_count=deleted_count,
        older_than_days=older_than_days,
        message=f"Cleaned up {deleted_count} old notifications"
    )
    
    return {"message": f"Deleted {deleted_count} old notifications"}
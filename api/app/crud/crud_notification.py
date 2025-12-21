"""
CRUD operations for notification system.

This module provides database operations for:
- Notifications
- Notification preferences
- Notification history
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.crud.base import CRUDBase
from app.models.notification import (
    Notification, 
    NotificationPreference, 
    NotificationHistory,
    NotificationType,
    NotificationStatus,
    NotificationChannel
)
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationHistoryCreate
)


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    """CRUD operations for notifications"""

    async def create_notification(
        self,
        db: AsyncSession,
        *,
        notification_data: NotificationCreate,
        created_by: Optional[str] = None
    ) -> Notification:
        """Create a new notification"""
        # Serialize context_data if it exists
        context_data_str = None
        if notification_data.context_data:
            import json
            try:
                # Handle both dict and already serialized string
                if isinstance(notification_data.context_data, dict):
                    context_data_str = json.dumps(notification_data.context_data)
                elif isinstance(notification_data.context_data, str):
                    # Validate it's valid JSON
                    json.loads(notification_data.context_data)
                    context_data_str = notification_data.context_data
                else:
                    # Convert other types to JSON
                    context_data_str = json.dumps(notification_data.context_data)
            except (TypeError, ValueError) as e:
                # If serialization fails, log error and set to None
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to serialize context_data: {e}, data: {notification_data.context_data}")
                context_data_str = None
        
        db_obj = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            entity_type=notification_data.entity_type,
            entity_id=notification_data.entity_id,
            channel=notification_data.channel,
            context_data=context_data_str,
            created_by=created_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_notifications(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a specific user"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if status:
            query = query.where(Notification.status == status)
        
        if notification_type:
            query = query.where(Notification.type == notification_type)
        
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def count_user_notifications(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None
    ) -> int:
        """Count notifications for a specific user"""
        query = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        
        if status:
            query = query.where(Notification.status == status)
        
        if notification_type:
            query = query.where(Notification.type == notification_type)
        
        result = await db.execute(query)
        return result.scalar()

    async def mark_as_read(
        self,
        db: AsyncSession,
        *,
        notification_id: str,
        user_id: str
    ) -> Optional[Notification]:
        """Mark a notification as read"""
        query = (
            update(Notification)
            .where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
            .values(
                status=NotificationStatus.read,
                read_at=datetime.utcnow()
            )
            .returning(Notification)
        )
        
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def mark_multiple_as_read(
        self,
        db: AsyncSession,
        *,
        notification_ids: List[str],
        user_id: str
    ) -> int:
        """Mark multiple notifications as read"""
        query = (
            update(Notification)
            .where(
                and_(
                    Notification.id.in_(notification_ids),
                    Notification.user_id == user_id
                )
            )
            .values(
                status=NotificationStatus.read,
                read_at=datetime.utcnow()
            )
        )
        
        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def mark_all_as_read(
        self,
        db: AsyncSession,
        *,
        user_id: str
    ) -> int:
        """Mark all unread notifications as read for a user"""
        query = (
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.status != NotificationStatus.read
                )
            )
            .values(
                status=NotificationStatus.read,
                read_at=datetime.utcnow()
            )
        )
        
        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def get_pending_notifications(
        self,
        db: AsyncSession,
        *,
        channel: Optional[NotificationChannel] = None,
        limit: int = 100
    ) -> List[Notification]:
        """Get pending notifications for processing"""
        query = select(Notification).where(Notification.status == NotificationStatus.pending)
        
        if channel:
            query = query.where(Notification.channel == channel)
        
        query = query.order_by(Notification.created_at).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def update_notification_status(
        self,
        db: AsyncSession,
        *,
        notification_id: str,
        status: NotificationStatus,
        sent_at: Optional[datetime] = None
    ) -> Optional[Notification]:
        """Update notification status"""
        values = {"status": status}
        if sent_at:
            values["sent_at"] = sent_at
        
        query = (
            update(Notification)
            .where(Notification.id == notification_id)
            .values(**values)
            .returning(Notification)
        )
        
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def delete_old_notifications(
        self,
        db: AsyncSession,
        *,
        older_than_days: int = 90
    ) -> int:
        """Delete notifications older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        query = delete(Notification).where(Notification.created_at < cutoff_date)
        
        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def get_notification_summary(
        self,
        db: AsyncSession,
        *,
        user_id: str
    ) -> Dict[str, Any]:
        """Get notification summary for a user"""
        # Count unread notifications by type
        unread_query = (
            select(
                Notification.type,
                func.count(Notification.id).label('count')
            )
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.status != NotificationStatus.read
                )
            )
            .group_by(Notification.type)
        )
        
        unread_result = await db.execute(unread_query)
        unread_by_type = {row.type: row.count for row in unread_result}
        
        # Get total unread count
        total_unread = sum(unread_by_type.values())
        
        # Get recent notifications (last 10)
        recent_query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(10)
        )
        
        recent_result = await db.execute(recent_query)
        recent_notifications = recent_result.scalars().all()
        
        return {
            "total_unread": total_unread,
            "unread_by_type": unread_by_type,
            "recent_notifications": recent_notifications
        }


class CRUDNotificationPreference(CRUDBase[NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate]):
    """CRUD operations for notification preferences"""

    async def get_user_preferences(
        self,
        db: AsyncSession,
        *,
        user_id: str
    ) -> List[NotificationPreference]:
        """Get all notification preferences for a user"""
        query = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_user_preference(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        notification_type: NotificationType
    ) -> Optional[NotificationPreference]:
        """Get specific notification preference for a user"""
        query = select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notification_type
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_user_preference(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        notification_type: NotificationType,
        preference_data: NotificationPreferenceUpdate
    ) -> Optional[NotificationPreference]:
        """Update notification preference for a user"""
        values = {}
        if preference_data.email_enabled is not None:
            values["email_enabled"] = preference_data.email_enabled
        if preference_data.in_app_enabled is not None:
            values["in_app_enabled"] = preference_data.in_app_enabled
        if preference_data.push_enabled is not None:
            values["push_enabled"] = preference_data.push_enabled
        
        if not values:
            return None
        
        values["updated_at"] = datetime.utcnow()
        
        query = (
            update(NotificationPreference)
            .where(
                and_(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.notification_type == notification_type
                )
            )
            .values(**values)
            .returning(NotificationPreference)
        )
        
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def create_default_preferences(
        self,
        db: AsyncSession,
        *,
        user_id: str
    ) -> List[NotificationPreference]:
        """Create default notification preferences for a new user"""
        preferences = []
        
        for notification_type in NotificationType:
            preference = NotificationPreference(
                user_id=user_id,
                notification_type=notification_type,
                email_enabled=True,
                in_app_enabled=True,
                push_enabled=False
            )
            preferences.append(preference)
            db.add(preference)
        
        await db.commit()
        
        for preference in preferences:
            await db.refresh(preference)
        
        return preferences

    async def check_user_preference(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        notification_type: NotificationType,
        channel: NotificationChannel
    ) -> bool:
        """Check if user has enabled notifications for specific type and channel"""
        preference = await self.get_user_preference(
            db, user_id=user_id, notification_type=notification_type
        )
        
        if not preference:
            return True  # Default to enabled if no preference found
        
        if channel == NotificationChannel.email:
            return preference.email_enabled
        elif channel == NotificationChannel.in_app:
            return preference.in_app_enabled
        elif channel == NotificationChannel.push:
            return preference.push_enabled
        
        return False


class CRUDNotificationHistory(CRUDBase[NotificationHistory, NotificationHistoryCreate, None]):
    """CRUD operations for notification history"""

    async def create_history_entry(
        self,
        db: AsyncSession,
        *,
        history_data: NotificationHistoryCreate
    ) -> NotificationHistory:
        """Create a notification history entry"""
        db_obj = NotificationHistory(**history_data.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_delivery_status(
        self,
        db: AsyncSession,
        *,
        history_id: str,
        status: NotificationStatus,
        delivered_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Optional[NotificationHistory]:
        """Update delivery status of a notification history entry"""
        values = {"status": status}
        
        if delivered_at:
            values["delivered_at"] = delivered_at
        if error_message:
            values["error_message"] = error_message
        if error_code:
            values["error_code"] = error_code
        if external_id:
            values["external_id"] = external_id
        
        query = (
            update(NotificationHistory)
            .where(NotificationHistory.id == history_id)
            .values(**values)
            .returning(NotificationHistory)
        )
        
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def get_notification_history(
        self,
        db: AsyncSession,
        *,
        notification_id: str
    ) -> List[NotificationHistory]:
        """Get delivery history for a notification"""
        query = (
            select(NotificationHistory)
            .where(NotificationHistory.notification_id == notification_id)
            .order_by(NotificationHistory.attempted_at.desc())
        )
        
        result = await db.execute(query)
        return result.scalars().all()


# Create instances
notification = CRUDNotification(Notification)
notification_preference = CRUDNotificationPreference(NotificationPreference)
notification_history = CRUDNotificationHistory(NotificationHistory)
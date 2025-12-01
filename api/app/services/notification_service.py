"""
Notification service for handling user notifications in the Worky API.

This service manages notifications for:
- @mentions in comments
- Bug assignments
- Status changes
- Test execution results
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import re

from app.models.user import User
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)


class NotificationService:
    """Service for handling user notifications"""
    
    @staticmethod
    def extract_mentions_from_text(text: str) -> List[str]:
        """
        Extract @mentions from text.
        
        Supports formats:
        - @username
        - @user_id
        
        Args:
            text: Text to extract mentions from
            
        Returns:
            List of mentioned usernames or user IDs
        """
        # Pattern to match @username or @user_id
        # Matches @word_characters (letters, numbers, underscores)
        pattern = r'@(\w+)'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Remove duplicates
    
    @staticmethod
    async def resolve_mentions_to_user_ids(
        db: AsyncSession,
        mentions: List[str]
    ) -> List[str]:
        """
        Resolve mention strings (usernames or IDs) to user IDs.
        
        Args:
            db: Database session
            mentions: List of usernames or user IDs from @mentions
            
        Returns:
            List of resolved user IDs
        """
        if not mentions:
            return []
        
        user_ids = []
        
        for mention in mentions:
            # Try to find user by username or ID
            result = await db.execute(
                select(User).where(
                    (User.username == mention) | (User.id == mention),
                    User.is_deleted == False
                )
            )
            user = result.scalar_one_or_none()
            
            if user:
                user_ids.append(str(user.id))
        
        return list(set(user_ids))  # Remove duplicates
    
    @staticmethod
    async def notify_mentioned_users(
        db: AsyncSession,
        mentioned_user_ids: List[str],
        entity_type: str,
        entity_id: str,
        comment_id: str,
        author_id: str,
        comment_text: str
    ) -> None:
        """
        Send notifications to users mentioned in a comment.
        
        Args:
            db: Database session
            mentioned_user_ids: List of user IDs who were mentioned
            entity_type: Type of entity ('bug' or 'test_case')
            entity_id: ID of the bug or test case
            comment_id: ID of the comment
            author_id: ID of the user who created the comment
            comment_text: Text of the comment (for preview)
        """
        if not mentioned_user_ids:
            return
        
        # Get author details
        author_result = await db.execute(
            select(User).where(User.id == author_id)
        )
        author = author_result.scalar_one_or_none()
        author_name = author.username if author else "Unknown User"
        
        # Create notification for each mentioned user
        for user_id in mentioned_user_ids:
            # Skip if user is mentioning themselves
            if user_id == author_id:
                continue
            
            # Get user details
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                continue
            
            # TODO: Implement actual notification delivery
            # For now, just log the notification
            # In a production system, this would:
            # 1. Create a notification record in the database
            # 2. Send an email notification
            # 3. Send a push notification
            # 4. Update in-app notification count
            
            logger.log_activity(
                action="send_mention_notification",
                entity_type=entity_type,
                entity_id=entity_id,
                comment_id=comment_id,
                mentioned_user_id=user_id,
                mentioned_user_name=user.username,
                author_id=author_id,
                author_name=author_name,
                message=f"{author_name} mentioned {user.username} in a comment on {entity_type} {entity_id}"
            )
            
            # Log notification details
            logger.info(
                f"Notification sent to user {user.username} (ID: {user_id}): "
                f"Mentioned by {author_name} in {entity_type} {entity_id}"
            )
    
    @staticmethod
    async def notify_bug_assignee(
        db: AsyncSession,
        bug_id: str,
        assignee_id: str,
        assigned_by_id: str,
        bug_title: str
    ) -> None:
        """
        Send notification to user when a bug is assigned to them.
        
        Args:
            db: Database session
            bug_id: ID of the bug
            assignee_id: ID of the user being assigned
            assigned_by_id: ID of the user who made the assignment
            bug_title: Title of the bug
        """
        # Get assignee details
        assignee_result = await db.execute(
            select(User).where(User.id == assignee_id)
        )
        assignee = assignee_result.scalar_one_or_none()
        
        if not assignee:
            return
        
        # Get assigner details
        assigner_result = await db.execute(
            select(User).where(User.id == assigned_by_id)
        )
        assigner = assigner_result.scalar_one_or_none()
        assigner_name = assigner.username if assigner else "Unknown User"
        
        # TODO: Implement actual notification delivery
        # For now, just log the notification
        
        logger.log_activity(
            action="send_bug_assignment_notification",
            entity_type="bug",
            entity_id=bug_id,
            assignee_id=assignee_id,
            assignee_name=assignee.username,
            assigned_by_id=assigned_by_id,
            assigned_by_name=assigner_name,
            message=f"Bug '{bug_title}' assigned to {assignee.username} by {assigner_name}"
        )
        
        logger.info(
            f"Assignment notification sent to user {assignee.username} (ID: {assignee_id}): "
            f"Bug {bug_id} assigned by {assigner_name}"
        )
    
    @staticmethod
    async def notify_bug_comment_stakeholders(
        db: AsyncSession,
        bug_id: str,
        comment_id: str,
        author_id: str,
        assignee_id: Optional[str],
        reporter_id: Optional[str]
    ) -> None:
        """
        Send notifications to bug stakeholders when a comment is added.
        
        Notifies:
        - Bug assignee (if different from comment author)
        - Bug reporter (if different from comment author)
        
        Args:
            db: Database session
            bug_id: ID of the bug
            comment_id: ID of the comment
            author_id: ID of the comment author
            assignee_id: ID of the bug assignee
            reporter_id: ID of the bug reporter
        """
        # Get author details
        author_result = await db.execute(
            select(User).where(User.id == author_id)
        )
        author = author_result.scalar_one_or_none()
        author_name = author.username if author else "Unknown User"
        
        # Notify assignee if different from author
        if assignee_id and assignee_id != author_id:
            assignee_result = await db.execute(
                select(User).where(User.id == assignee_id)
            )
            assignee = assignee_result.scalar_one_or_none()
            
            if assignee:
                logger.log_activity(
                    action="send_bug_comment_notification",
                    entity_type="bug",
                    entity_id=bug_id,
                    comment_id=comment_id,
                    recipient_id=assignee_id,
                    recipient_name=assignee.username,
                    author_id=author_id,
                    author_name=author_name,
                    message=f"{author_name} commented on bug {bug_id} assigned to {assignee.username}"
                )
        
        # Notify reporter if different from author and assignee
        if reporter_id and reporter_id != author_id and reporter_id != assignee_id:
            reporter_result = await db.execute(
                select(User).where(User.id == reporter_id)
            )
            reporter = reporter_result.scalar_one_or_none()
            
            if reporter:
                logger.log_activity(
                    action="send_bug_comment_notification",
                    entity_type="bug",
                    entity_id=bug_id,
                    comment_id=comment_id,
                    recipient_id=reporter_id,
                    recipient_name=reporter.username,
                    author_id=author_id,
                    author_name=author_name,
                    message=f"{author_name} commented on bug {bug_id} reported by {reporter.username}"
                )
    
    @staticmethod
    async def send_reminder_notification(
        db: AsyncSession,
        reminder_id: str,
        user_id: str,
        entity_type: str,
        entity_id: str,
        message: Optional[str] = None
    ) -> bool:
        """
        Send a reminder notification to a user.
        
        This method handles the delivery of reminder notifications.
        In a production system, this would:
        1. Send an email notification
        2. Send a push notification
        3. Create an in-app notification
        4. Update notification counters
        
        Args:
            db: Database session
            reminder_id: ID of the reminder
            user_id: ID of the user to notify
            entity_type: Type of entity ("task", "bug", "project")
            entity_id: ID of the entity
            message: Optional custom message for the reminder
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        # Get user details
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.error(f"Cannot send reminder notification: User {user_id} not found")
            return False
        
        # TODO: Implement actual notification delivery
        # For now, just log the notification
        # In a production system, this would:
        # 1. Send email via email service (SendGrid, AWS SES, etc.)
        # 2. Send push notification via push service (Firebase, OneSignal, etc.)
        # 3. Create in-app notification record
        # 4. Send webhook to external systems if configured
        
        notification_message = message or f"Reminder for {entity_type} {entity_id}"
        
        logger.log_activity(
            action="send_reminder_notification",
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_id=reminder_id,
            user_id=user_id,
            user_name=user.username,
            message=notification_message
        )
        
        logger.info(
            f"Reminder notification sent to user {user.username} (ID: {user_id}): "
            f"{notification_message}"
        )
        
        return True
    
    @staticmethod
    async def process_pending_reminders(
        db: AsyncSession,
        reminder_crud
    ) -> int:
        """
        Process all pending reminders that are due.
        
        This method should be called by a background job or scheduled task.
        It fetches all pending reminders, sends notifications, and marks them as sent.
        
        Args:
            db: Database session
            reminder_crud: CRUD instance for reminder operations
            
        Returns:
            Number of reminders processed
        """
        from datetime import datetime
        
        # Get all pending reminders that are due
        pending_reminders = await reminder_crud.get_pending_reminders(
            db=db,
            before=datetime.now(),
            limit=1000  # Process up to 1000 reminders at a time
        )
        
        processed_count = 0
        successfully_sent = []
        
        for reminder in pending_reminders:
            try:
                # Send notification
                success = await NotificationService.send_reminder_notification(
                    db=db,
                    reminder_id=reminder.id,
                    user_id=reminder.user_id,
                    entity_type=reminder.entity_type,
                    entity_id=reminder.entity_id,
                    message=reminder.message
                )
                
                if success:
                    successfully_sent.append(reminder.id)
                    processed_count += 1
                    
            except Exception as e:
                logger.error(
                    f"Failed to send reminder notification for reminder {reminder.id}: {str(e)}",
                    reminder_id=reminder.id,
                    user_id=reminder.user_id,
                    error=str(e)
                )
        
        # Mark successfully sent reminders as sent
        if successfully_sent:
            await reminder_crud.mark_multiple_as_sent(
                db=db,
                reminder_ids=successfully_sent
            )
        
        logger.info(
            f"Processed {processed_count} pending reminders",
            processed_count=processed_count,
            total_pending=len(pending_reminders)
        )
        
        return processed_count


# Create singleton instance
notification_service = NotificationService()

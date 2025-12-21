"""
Notification service for handling user notifications in the Worky API.

This service manages notifications for:
- @mentions in comments
- Bug assignments
- Status changes
- Test execution results
- Team assignment notifications
- Team membership changes
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import re
from datetime import datetime

from app.models.user import User
from app.models.notification import (
    Notification, 
    NotificationPreference, 
    NotificationHistory,
    NotificationType, 
    NotificationStatus, 
    NotificationChannel
)
from app.crud.crud_notification import notification as crud_notification
from app.crud.crud_notification import notification_preference as crud_notification_preference
from app.crud.crud_notification import notification_history as crud_notification_history
from app.schemas.notification import (
    NotificationCreate, 
    NotificationHistoryCreate,
    AssignmentNotificationContext,
    TeamNotificationContext,
    EmailNotificationData
)
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


    # Assignment notification methods
    @staticmethod
    async def notify_assignment_created(
        db: AsyncSession,
        assigned_user_id: str,
        entity_type: str,
        entity_id: str,
        entity_title: Optional[str],
        assigned_by_id: str,
        assignment_type: str,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None
    ) -> Optional[Notification]:
        """
        Send notification when a user is assigned to a hierarchy element.
        
        Args:
            db: Database session
            assigned_user_id: ID of the user being assigned
            entity_type: Type of entity being assigned
            entity_id: ID of the entity
            entity_title: Title/name of the entity
            assigned_by_id: ID of the user making the assignment
            assignment_type: Type of assignment (owner, developer, etc.)
            project_id: Optional project ID for context
            project_name: Optional project name for context
            
        Returns:
            Created notification or None if user has disabled this notification type
        """
        # Check if user has enabled this notification type
        preference_enabled = await crud_notification_preference.check_user_preference(
            db, 
            user_id=assigned_user_id, 
            notification_type=NotificationType.assignment_created,
            channel=NotificationChannel.in_app
        )
        
        if not preference_enabled:
            logger.info(f"Assignment notification disabled for user {assigned_user_id}")
            return None
        
        # Get assigned user and assigner details
        assigned_user = await db.get(User, assigned_user_id)
        assigner = await db.get(User, assigned_by_id)
        
        if not assigned_user or not assigner:
            logger.error(f"User not found: assigned_user={assigned_user_id}, assigner={assigned_by_id}")
            return None
        
        # Create notification context
        context = AssignmentNotificationContext(
            assignment_id=f"{entity_type}_{entity_id}_{assigned_user_id}",
            entity_type=entity_type,
            entity_id=entity_id,
            entity_title=entity_title,
            assigned_by=assigned_by_id,
            assigned_by_name=assigner.full_name,
            assignment_type=assignment_type,
            project_id=project_id,
            project_name=project_name
        )
        
        # Create notification
        title = f"New Assignment: {entity_type.title()}"
        message = f"You have been assigned as {assignment_type} to {entity_type} '{entity_title or entity_id}' by {assigner.full_name}"
        
        if project_name:
            message += f" in project '{project_name}'"
        
        notification_data = NotificationCreate(
            user_id=assigned_user_id,
            type=NotificationType.assignment_created,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            channel=NotificationChannel.in_app,
            context_data=context.dict()
        )
        
        notification = await crud_notification.create_notification(
            db, notification_data=notification_data, created_by=assigned_by_id
        )
        
        # Send email notification if enabled
        await NotificationService._send_email_notification_if_enabled(
            db, notification, assigned_user, context
        )
        
        logger.log_activity(
            action="assignment_notification_created",
            entity_type=entity_type,
            entity_id=entity_id,
            assigned_user_id=assigned_user_id,
            assigned_by_id=assigned_by_id,
            notification_id=notification.id,
            message=f"Assignment notification sent to {assigned_user.full_name}"
        )
        
        return notification

    @staticmethod
    async def notify_assignment_removed(
        db: AsyncSession,
        removed_user_id: str,
        entity_type: str,
        entity_id: str,
        entity_title: Optional[str],
        removed_by_id: str,
        assignment_type: str,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None
    ) -> Optional[Notification]:
        """
        Send notification when a user's assignment is removed.
        
        Args:
            db: Database session
            removed_user_id: ID of the user whose assignment was removed
            entity_type: Type of entity
            entity_id: ID of the entity
            entity_title: Title/name of the entity
            removed_by_id: ID of the user removing the assignment
            assignment_type: Type of assignment that was removed
            project_id: Optional project ID for context
            project_name: Optional project name for context
            
        Returns:
            Created notification or None if user has disabled this notification type
        """
        # Check if user has enabled this notification type
        preference_enabled = await crud_notification_preference.check_user_preference(
            db, 
            user_id=removed_user_id, 
            notification_type=NotificationType.assignment_removed,
            channel=NotificationChannel.in_app
        )
        
        if not preference_enabled:
            logger.info(f"Assignment removal notification disabled for user {removed_user_id}")
            return None
        
        # Get user details
        removed_user = await db.get(User, removed_user_id)
        remover = await db.get(User, removed_by_id)
        
        if not removed_user or not remover:
            logger.error(f"User not found: removed_user={removed_user_id}, remover={removed_by_id}")
            return None
        
        # Create notification context
        context = AssignmentNotificationContext(
            assignment_id=f"{entity_type}_{entity_id}_{removed_user_id}",
            entity_type=entity_type,
            entity_id=entity_id,
            entity_title=entity_title,
            assigned_by=removed_by_id,
            assigned_by_name=remover.full_name,
            assignment_type=assignment_type,
            project_id=project_id,
            project_name=project_name
        )
        
        # Create notification
        title = f"Assignment Removed: {entity_type.title()}"
        message = f"Your assignment as {assignment_type} to {entity_type} '{entity_title or entity_id}' has been removed by {remover.full_name}"
        
        if project_name:
            message += f" in project '{project_name}'"
        
        notification_data = NotificationCreate(
            user_id=removed_user_id,
            type=NotificationType.assignment_removed,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            channel=NotificationChannel.in_app,
            context_data=context.dict()
        )
        
        notification = await crud_notification.create_notification(
            db, notification_data=notification_data, created_by=removed_by_id
        )
        
        # Send email notification if enabled
        await NotificationService._send_email_notification_if_enabled(
            db, notification, removed_user, context
        )
        
        logger.log_activity(
            action="assignment_removal_notification_created",
            entity_type=entity_type,
            entity_id=entity_id,
            removed_user_id=removed_user_id,
            removed_by_id=removed_by_id,
            notification_id=notification.id,
            message=f"Assignment removal notification sent to {removed_user.full_name}"
        )
        
        return notification

    @staticmethod
    async def notify_team_member_added(
        db: AsyncSession,
        added_user_id: str,
        team_id: str,
        team_name: str,
        project_id: str,
        project_name: Optional[str],
        added_by_id: str,
        role: Optional[str] = None
    ) -> Optional[Notification]:
        """
        Send notification when a user is added to a team.
        
        Args:
            db: Database session
            added_user_id: ID of the user added to the team
            team_id: ID of the team
            team_name: Name of the team
            project_id: ID of the project
            project_name: Name of the project
            added_by_id: ID of the user who added the member
            role: Role of the user in the team
            
        Returns:
            Created notification or None if user has disabled this notification type
        """
        # Check if user has enabled this notification type
        preference_enabled = await crud_notification_preference.check_user_preference(
            db, 
            user_id=added_user_id, 
            notification_type=NotificationType.team_member_added,
            channel=NotificationChannel.in_app
        )
        
        if not preference_enabled:
            logger.info(f"Team member added notification disabled for user {added_user_id}")
            return None
        
        # Get user details
        added_user = await db.get(User, added_user_id)
        adder = await db.get(User, added_by_id)
        
        if not added_user or not adder:
            logger.error(f"User not found: added_user={added_user_id}, adder={added_by_id}")
            return None
        
        # Create notification context
        context = TeamNotificationContext(
            team_id=team_id,
            team_name=team_name,
            project_id=project_id,
            project_name=project_name,
            action_by=added_by_id,
            action_by_name=adder.full_name,
            role=role
        )
        
        # Create notification
        title = f"Added to Team: {team_name}"
        message = f"You have been added to team '{team_name}' by {adder.full_name}"
        
        if role:
            message += f" with role '{role}'"
        
        if project_name:
            message += f" for project '{project_name}'"
        
        notification_data = NotificationCreate(
            user_id=added_user_id,
            type=NotificationType.team_member_added,
            title=title,
            message=message,
            entity_type="team",
            entity_id=team_id,
            channel=NotificationChannel.in_app,
            context_data=context.dict()
        )
        
        notification = await crud_notification.create_notification(
            db, notification_data=notification_data, created_by=added_by_id
        )
        
        # Send email notification if enabled
        await NotificationService._send_email_notification_if_enabled(
            db, notification, added_user, context
        )
        
        logger.log_activity(
            action="team_member_added_notification_created",
            team_id=team_id,
            added_user_id=added_user_id,
            added_by_id=added_by_id,
            notification_id=notification.id,
            message=f"Team member added notification sent to {added_user.full_name}"
        )
        
        return notification

    @staticmethod
    async def notify_team_member_removed(
        db: AsyncSession,
        removed_user_id: str,
        team_id: str,
        team_name: str,
        project_id: str,
        project_name: Optional[str],
        removed_by_id: str
    ) -> Optional[Notification]:
        """
        Send notification when a user is removed from a team.
        
        Args:
            db: Database session
            removed_user_id: ID of the user removed from the team
            team_id: ID of the team
            team_name: Name of the team
            project_id: ID of the project
            project_name: Name of the project
            removed_by_id: ID of the user who removed the member
            
        Returns:
            Created notification or None if user has disabled this notification type
        """
        # Check if user has enabled this notification type
        preference_enabled = await crud_notification_preference.check_user_preference(
            db, 
            user_id=removed_user_id, 
            notification_type=NotificationType.team_member_removed,
            channel=NotificationChannel.in_app
        )
        
        if not preference_enabled:
            logger.info(f"Team member removed notification disabled for user {removed_user_id}")
            return None
        
        # Get user details
        removed_user = await db.get(User, removed_user_id)
        remover = await db.get(User, removed_by_id)
        
        if not removed_user or not remover:
            logger.error(f"User not found: removed_user={removed_user_id}, remover={removed_by_id}")
            return None
        
        # Create notification context
        context = TeamNotificationContext(
            team_id=team_id,
            team_name=team_name,
            project_id=project_id,
            project_name=project_name,
            action_by=removed_by_id,
            action_by_name=remover.full_name
        )
        
        # Create notification
        title = f"Removed from Team: {team_name}"
        message = f"You have been removed from team '{team_name}' by {remover.full_name}"
        
        if project_name:
            message += f" for project '{project_name}'"
        
        notification_data = NotificationCreate(
            user_id=removed_user_id,
            type=NotificationType.team_member_removed,
            title=title,
            message=message,
            entity_type="team",
            entity_id=team_id,
            channel=NotificationChannel.in_app,
            context_data=context.dict()
        )
        
        notification = await crud_notification.create_notification(
            db, notification_data=notification_data, created_by=removed_by_id
        )
        
        # Send email notification if enabled
        await NotificationService._send_email_notification_if_enabled(
            db, notification, removed_user, context
        )
        
        logger.log_activity(
            action="team_member_removed_notification_created",
            team_id=team_id,
            removed_user_id=removed_user_id,
            removed_by_id=removed_by_id,
            notification_id=notification.id,
            message=f"Team member removed notification sent to {removed_user.full_name}"
        )
        
        return notification

    @staticmethod
    async def notify_assignment_conflict(
        db: AsyncSession,
        stakeholder_user_ids: List[str],
        entity_type: str,
        entity_id: str,
        entity_title: Optional[str],
        conflict_description: str,
        reported_by_id: str,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None
    ) -> List[Notification]:
        """
        Send notifications about assignment conflicts to relevant stakeholders.
        
        Args:
            db: Database session
            stakeholder_user_ids: List of user IDs to notify
            entity_type: Type of entity with conflict
            entity_id: ID of the entity
            entity_title: Title/name of the entity
            conflict_description: Description of the conflict
            reported_by_id: ID of the user reporting the conflict
            project_id: Optional project ID for context
            project_name: Optional project name for context
            
        Returns:
            List of created notifications
        """
        notifications = []
        
        # Get reporter details
        reporter = await db.get(User, reported_by_id)
        if not reporter:
            logger.error(f"Reporter user not found: {reported_by_id}")
            return notifications
        
        for user_id in stakeholder_user_ids:
            # Check if user has enabled this notification type
            preference_enabled = await crud_notification_preference.check_user_preference(
                db, 
                user_id=user_id, 
                notification_type=NotificationType.assignment_conflict,
                channel=NotificationChannel.in_app
            )
            
            if not preference_enabled:
                logger.info(f"Assignment conflict notification disabled for user {user_id}")
                continue
            
            # Get user details
            user = await db.get(User, user_id)
            if not user:
                logger.error(f"Stakeholder user not found: {user_id}")
                continue
            
            # Create notification context
            context = AssignmentNotificationContext(
                assignment_id=f"conflict_{entity_type}_{entity_id}",
                entity_type=entity_type,
                entity_id=entity_id,
                entity_title=entity_title,
                assigned_by=reported_by_id,
                assigned_by_name=reporter.full_name,
                assignment_type="conflict",
                project_id=project_id,
                project_name=project_name
            )
            
            # Create notification
            title = f"Assignment Conflict: {entity_type.title()}"
            message = f"Assignment conflict detected for {entity_type} '{entity_title or entity_id}': {conflict_description}"
            
            if project_name:
                message += f" in project '{project_name}'"
            
            notification_data = NotificationCreate(
                user_id=user_id,
                type=NotificationType.assignment_conflict,
                title=title,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
                channel=NotificationChannel.in_app,
                context_data=context.dict()
            )
            
            notification = await crud_notification.create_notification(
                db, notification_data=notification_data, created_by=reported_by_id
            )
            
            notifications.append(notification)
            
            # Send email notification if enabled
            await NotificationService._send_email_notification_if_enabled(
                db, notification, user, context
            )
        
        logger.log_activity(
            action="assignment_conflict_notifications_created",
            entity_type=entity_type,
            entity_id=entity_id,
            stakeholder_count=len(notifications),
            reported_by_id=reported_by_id,
            message=f"Assignment conflict notifications sent to {len(notifications)} stakeholders"
        )
        
        return notifications

    @staticmethod
    async def notify_bulk_assignment_completed(
        db: AsyncSession,
        user_id: str,
        successful_count: int,
        failed_count: int,
        total_count: int,
        initiated_by_id: str
    ) -> Optional[Notification]:
        """
        Send notification when bulk assignment operation completes.
        
        Args:
            db: Database session
            user_id: ID of the user to notify (usually the one who initiated)
            successful_count: Number of successful assignments
            failed_count: Number of failed assignments
            total_count: Total number of assignments attempted
            initiated_by_id: ID of the user who initiated the bulk operation
            
        Returns:
            Created notification or None if user has disabled this notification type
        """
        # Check if user has enabled this notification type
        preference_enabled = await crud_notification_preference.check_user_preference(
            db, 
            user_id=user_id, 
            notification_type=NotificationType.bulk_assignment_completed,
            channel=NotificationChannel.in_app
        )
        
        if not preference_enabled:
            logger.info(f"Bulk assignment notification disabled for user {user_id}")
            return None
        
        # Get user details
        user = await db.get(User, user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            return None
        
        # Create notification
        title = "Bulk Assignment Completed"
        message = f"Bulk assignment operation completed: {successful_count}/{total_count} successful"
        
        if failed_count > 0:
            message += f", {failed_count} failed"
        
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.bulk_assignment_completed,
            title=title,
            message=message,
            entity_type="bulk_assignment",
            entity_id=f"bulk_{initiated_by_id}_{datetime.utcnow().timestamp()}",
            channel=NotificationChannel.in_app,
            context_data={
                "successful_count": successful_count,
                "failed_count": failed_count,
                "total_count": total_count,
                "initiated_by": initiated_by_id
            }
        )
        
        notification = await crud_notification.create_notification(
            db, notification_data=notification_data, created_by=initiated_by_id
        )
        
        logger.log_activity(
            action="bulk_assignment_notification_created",
            user_id=user_id,
            successful_count=successful_count,
            failed_count=failed_count,
            total_count=total_count,
            notification_id=notification.id,
            message=f"Bulk assignment completion notification sent to {user.full_name}"
        )
        
        return notification

    @staticmethod
    async def _send_email_notification_if_enabled(
        db: AsyncSession,
        notification: Notification,
        user: User,
        context: Any
    ) -> Optional[NotificationHistory]:
        """
        Send email notification if user has enabled email notifications.
        
        Args:
            db: Database session
            notification: The notification to send via email
            user: The user to send email to
            context: Context data for the notification
            
        Returns:
            NotificationHistory entry if email was sent, None otherwise
        """
        # Check if user has enabled email notifications for this type
        preference_enabled = await crud_notification_preference.check_user_preference(
            db, 
            user_id=user.id, 
            notification_type=notification.type,
            channel=NotificationChannel.email
        )
        
        if not preference_enabled:
            return None
        
        # Create history entry for email attempt
        history_data = NotificationHistoryCreate(
            notification_id=notification.id,
            channel=NotificationChannel.email,
            status=NotificationStatus.pending
        )
        
        history = await crud_notification_history.create_history_entry(
            db, history_data=history_data
        )
        
        try:
            # TODO: Implement actual email sending
            # This would integrate with an email service like SendGrid, AWS SES, etc.
            
            # For now, just log the email notification
            logger.log_activity(
                action="email_notification_sent",
                notification_id=notification.id,
                user_id=user.id,
                user_email=user.email,
                notification_type=notification.type.value,
                message=f"Email notification sent to {user.email}"
            )
            
            # Update history as sent
            await crud_notification_history.update_delivery_status(
                db,
                history_id=history.id,
                status=NotificationStatus.sent,
                delivered_at=datetime.utcnow()
            )
            
            return history
            
        except Exception as e:
            logger.error(
                f"Failed to send email notification: {str(e)}",
                notification_id=notification.id,
                user_id=user.id,
                error=str(e)
            )
            
            # Update history as failed
            await crud_notification_history.update_delivery_status(
                db,
                history_id=history.id,
                status=NotificationStatus.failed,
                error_message=str(e),
                error_code="EMAIL_SEND_FAILED"
            )
            
            return history

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user with filtering options"""
        return await crud_notification.get_user_notifications(
            db,
            user_id=user_id,
            status=status,
            notification_type=notification_type,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def mark_notification_as_read(
        db: AsyncSession,
        notification_id: str,
        user_id: str
    ) -> Optional[Notification]:
        """Mark a notification as read"""
        return await crud_notification.mark_as_read(
            db, notification_id=notification_id, user_id=user_id
        )

    @staticmethod
    async def get_notification_summary(
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """Get notification summary for a user"""
        return await crud_notification.get_notification_summary(db, user_id=user_id)

    @staticmethod
    async def update_notification_preferences(
        db: AsyncSession,
        user_id: str,
        notification_type: NotificationType,
        email_enabled: Optional[bool] = None,
        in_app_enabled: Optional[bool] = None,
        push_enabled: Optional[bool] = None
    ) -> Optional[NotificationPreference]:
        """Update notification preferences for a user"""
        from app.schemas.notification import NotificationPreferenceUpdate
        
        preference_data = NotificationPreferenceUpdate(
            email_enabled=email_enabled,
            in_app_enabled=in_app_enabled,
            push_enabled=push_enabled
        )
        
        return await crud_notification_preference.update_user_preference(
            db,
            user_id=user_id,
            notification_type=notification_type,
            preference_data=preference_data
        )


# Create singleton instance
notification_service = NotificationService()

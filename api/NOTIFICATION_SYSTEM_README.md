# Assignment Notification System

This document describes the notification system implemented for the team assignment system.

## Overview

The notification system provides comprehensive notification capabilities for assignment and team management operations, including:

- Assignment creation and removal notifications
- Team membership change notifications
- Assignment conflict notifications
- Bulk operation completion notifications
- Email and in-app notification support
- User notification preferences management
- Notification history tracking

## Components

### 1. Database Models

- **Notification**: Stores individual notifications
- **NotificationPreference**: User preferences for notification types and channels
- **NotificationHistory**: Tracks notification delivery attempts

### 2. Notification Types

- `assignment_created`: User assigned to hierarchy element
- `assignment_removed`: User's assignment removed
- `team_member_added`: User added to team
- `team_member_removed`: User removed from team
- `assignment_conflict`: Assignment conflicts detected
- `bulk_assignment_completed`: Bulk assignment operation completed
- `bulk_assignment_failed`: Bulk assignment operation failed

### 3. Notification Channels

- `in_app`: In-application notifications
- `email`: Email notifications
- `push`: Push notifications (future implementation)

### 4. API Endpoints

- `GET /notifications/`: Get user notifications with filtering and pagination
- `GET /notifications/summary`: Get notification summary and counts
- `PUT /notifications/{id}/read`: Mark notification as read
- `PUT /notifications/read-all`: Mark all notifications as read
- `GET /notifications/preferences`: Get user notification preferences
- `PUT /notifications/preferences/{type}`: Update notification preferences
- `POST /notifications/bulk`: Send bulk notifications

## Usage

### Automatic Notifications

The system automatically sends notifications when:

1. **Assignment Operations** (via AssignmentService):
   - User assigned to hierarchy element
   - User's assignment removed

2. **Team Operations** (via TeamService):
   - User added to team
   - User removed from team

### Manual Notifications

Use the NotificationService to send custom notifications:

```python
from app.services.notification_service import notification_service

# Send assignment notification
await notification_service.notify_assignment_created(
    db=db,
    assigned_user_id="USR-001",
    entity_type="task",
    entity_id="TSK-001",
    entity_title="Implement feature X",
    assigned_by_id="USR-002",
    assignment_type="developer",
    project_id="PRJ-001",
    project_name="Project Alpha"
)
```

### User Preferences

Users can configure notification preferences for each notification type and channel:

```python
# Update user preferences
await notification_service.update_notification_preferences(
    db=db,
    user_id="USR-001",
    notification_type=NotificationType.assignment_created,
    email_enabled=True,
    in_app_enabled=True,
    push_enabled=False
)
```

### Getting Notifications

```python
# Get user notifications
notifications = await notification_service.get_user_notifications(
    db=db,
    user_id="USR-001",
    status=NotificationStatus.pending,
    skip=0,
    limit=20
)

# Get notification summary
summary = await notification_service.get_notification_summary(
    db=db,
    user_id="USR-001"
)
```

## Database Schema

The notification system adds three new tables:

1. **notifications**: Stores notification records
2. **notification_preferences**: User preferences per notification type
3. **notification_history**: Delivery attempt tracking

## Integration

The notification system is integrated with:

- **AssignmentService**: Automatic notifications for assignment operations
- **TeamService**: Automatic notifications for team membership changes
- **API Router**: RESTful endpoints for notification management
- **User Model**: Relationships for notifications and preferences

## Configuration

Default notification preferences are automatically created for new users via database triggers. Users can modify these preferences through the API or UI.

## Future Enhancements

- Push notification implementation
- Email template system
- Notification batching and digest emails
- Advanced notification rules and filters
- Webhook notifications for external systems
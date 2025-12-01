# Reminder System

## Overview

The reminder system allows users to create reminders for tasks, bugs, and projects. Reminders are processed by a background job that sends notifications when they are due.

## Components

### 1. CRUD Operations (`api/app/crud/crud_reminder.py`)

Provides database operations for reminders:

- `create()` - Create a new reminder
- `get_by_user()` - Get all reminders for a user
- `get_pending_reminders()` - Get unsent reminders that are due
- `get_by_entity()` - Get reminders for a specific entity (task, bug, project)
- `get_upcoming_reminders()` - Get reminders due within a time window
- `mark_as_sent()` - Mark a single reminder as sent
- `mark_multiple_as_sent()` - Batch mark reminders as sent
- `delete_reminder()` - Delete a reminder (hard delete)

### 2. Notification Service (`api/app/services/notification_service.py`)

Handles reminder notifications:

- `send_reminder_notification()` - Send notification for a single reminder
- `process_pending_reminders()` - Process all pending reminders (called by background job)

### 3. Background Job (`api/app/services/reminder_background_job.py`)

Periodically checks for and processes pending reminders:

- Runs at configurable intervals (default: 5 minutes)
- Fetches pending reminders that are due
- Sends notifications via the notification service
- Marks successfully sent reminders as sent

## Usage

### Creating a Reminder

```python
from app.crud.crud_reminder import reminder
from app.schemas.chat import ReminderCreate
from datetime import datetime, timedelta

# Create a reminder
reminder_data = ReminderCreate(
    entity_type="task",
    entity_id="TSK-123",
    message="Review the implementation",
    remind_at=datetime.now() + timedelta(hours=2),
    created_via="chat"
)

new_reminder = await reminder.create(
    db=db,
    obj_in=reminder_data,
    user_id="USR-001"
)
```

### Getting User Reminders

```python
# Get all reminders for a user
user_reminders = await reminder.get_by_user(
    db=db,
    user_id="USR-001",
    skip=0,
    limit=100
)

# Get upcoming reminders (next 24 hours)
upcoming = await reminder.get_upcoming_reminders(
    db=db,
    user_id="USR-001",
    hours_ahead=24
)
```

### Getting Pending Reminders

```python
from datetime import datetime

# Get all pending reminders that are due
pending = await reminder.get_pending_reminders(
    db=db,
    before=datetime.now(),
    limit=100
)

# Get pending reminders for a specific user
user_pending = await reminder.get_pending_reminders(
    db=db,
    user_id="USR-001",
    before=datetime.now()
)
```

### Marking Reminders as Sent

```python
# Mark a single reminder as sent
await reminder.mark_as_sent(
    db=db,
    reminder_id="REM-001"
)

# Mark multiple reminders as sent (batch operation)
await reminder.mark_multiple_as_sent(
    db=db,
    reminder_ids=["REM-001", "REM-002", "REM-003"]
)
```

### Deleting a Reminder

```python
# Delete a reminder (only owner can delete)
deleted = await reminder.delete_reminder(
    db=db,
    reminder_id="REM-001",
    user_id="USR-001"  # Must match the reminder owner
)
```

## Running the Background Job

### Option 1: Standalone Script

Run the background job as a separate process:

```bash
# Run with default interval (5 minutes)
python api/run_reminder_job.py

# Run with custom interval (10 minutes)
python api/run_reminder_job.py --interval 10
```

### Option 2: Docker/Systemd Service

Create a systemd service file (`/etc/systemd/system/worky-reminder-job.service`):

```ini
[Unit]
Description=Worky Reminder Background Job
After=network.target postgresql.service

[Service]
Type=simple
User=worky
WorkingDirectory=/path/to/worky/api
Environment="PYTHONPATH=/path/to/worky/api"
ExecStart=/usr/bin/python3 /path/to/worky/api/run_reminder_job.py --interval 5
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable worky-reminder-job
sudo systemctl start worky-reminder-job
sudo systemctl status worky-reminder-job
```

### Option 3: Integrate with Main Application

Add to your FastAPI startup event in `api/app/main.py`:

```python
from app.services.reminder_background_job import reminder_background_job
import asyncio

@app.on_event("startup")
async def startup_event():
    # Start reminder background job
    await reminder_background_job.initialize()
    asyncio.create_task(
        reminder_background_job.run_periodically(interval_minutes=5)
    )

@app.on_event("shutdown")
async def shutdown_event():
    # Stop reminder background job
    reminder_background_job.stop()
    await reminder_background_job.close()
```

## Notification Delivery

Currently, the notification service logs reminder notifications. In a production system, you would implement actual notification delivery:

### Email Notifications

```python
# In notification_service.py, update send_reminder_notification()
import smtplib
from email.mime.text import MIMEText

async def send_reminder_notification(...):
    # ... existing code ...
    
    # Send email
    msg = MIMEText(notification_message)
    msg['Subject'] = f'Reminder: {entity_type} {entity_id}'
    msg['From'] = 'noreply@worky.com'
    msg['To'] = user.email
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('username', 'password')
        server.send_message(msg)
```

### Push Notifications

```python
# Using Firebase Cloud Messaging
from firebase_admin import messaging

async def send_reminder_notification(...):
    # ... existing code ...
    
    # Send push notification
    message = messaging.Message(
        notification=messaging.Notification(
            title=f'Reminder: {entity_type}',
            body=notification_message,
        ),
        token=user.fcm_token,
    )
    
    response = messaging.send(message)
```

### Webhook Integration

```python
# Send to external systems (Slack, Teams, etc.)
import httpx

async def send_reminder_notification(...):
    # ... existing code ...
    
    # Send webhook
    async with httpx.AsyncClient() as client:
        await client.post(
            'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
            json={
                'text': f'Reminder for {user.username}: {notification_message}'
            }
        )
```

## Database Schema

The `reminders` table has the following structure:

```sql
CREATE TABLE reminders (
    id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,  -- 'task', 'bug', 'project'
    entity_id VARCHAR(20) NOT NULL,
    message TEXT,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    created_via VARCHAR(20) DEFAULT 'chat',  -- 'chat', 'ui', 'api'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_remind_at ON reminders(remind_at);
CREATE INDEX idx_reminders_is_sent ON reminders(is_sent);
```

## API Integration

The reminder CRUD operations can be integrated into API endpoints:

```python
from fastapi import APIRouter, Depends
from app.crud.crud_reminder import reminder
from app.schemas.chat import ReminderCreate, ReminderResponse

router = APIRouter()

@router.post("/reminders", response_model=ReminderResponse)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new reminder"""
    return await reminder.create(
        db=db,
        obj_in=reminder_data,
        user_id=current_user.id
    )

@router.get("/reminders", response_model=List[ReminderResponse])
async def get_user_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all reminders for the current user"""
    return await reminder.get_by_user(
        db=db,
        user_id=current_user.id
    )

@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a reminder"""
    deleted = await reminder.delete_reminder(
        db=db,
        reminder_id=reminder_id,
        user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted successfully"}
```

## Monitoring

Monitor the reminder system using logs:

```bash
# View reminder job logs
tail -f api/logs/api.log | grep "reminder"

# Check processed reminders
grep "Processed.*pending reminders" api/logs/api.log

# Check for errors
grep "ERROR.*reminder" api/logs/api.log
```

## Testing

Test the reminder system:

```python
import pytest
from datetime import datetime, timedelta
from app.crud.crud_reminder import reminder
from app.schemas.chat import ReminderCreate

@pytest.mark.asyncio
async def test_create_reminder(db_session):
    """Test creating a reminder"""
    reminder_data = ReminderCreate(
        entity_type="task",
        entity_id="TSK-123",
        message="Test reminder",
        remind_at=datetime.now() + timedelta(hours=1),
        created_via="api"
    )
    
    result = await reminder.create(
        db=db_session,
        obj_in=reminder_data,
        user_id="USR-001"
    )
    
    assert result.id is not None
    assert result.entity_type == "task"
    assert result.is_sent == False

@pytest.mark.asyncio
async def test_get_pending_reminders(db_session):
    """Test getting pending reminders"""
    # Create a reminder that's due
    reminder_data = ReminderCreate(
        entity_type="bug",
        entity_id="BUG-456",
        message="Overdue reminder",
        remind_at=datetime.now() - timedelta(minutes=5),
        created_via="api"
    )
    
    await reminder.create(
        db=db_session,
        obj_in=reminder_data,
        user_id="USR-001"
    )
    
    # Get pending reminders
    pending = await reminder.get_pending_reminders(
        db=db_session,
        before=datetime.now()
    )
    
    assert len(pending) > 0
    assert all(r.is_sent == False for r in pending)
```

## Requirements Satisfied

This implementation satisfies the following requirements from the chat assistant spec:

- **Requirement 3.2**: SET_REMINDER action with validation
- **Requirement 3.3**: Action confirmation and execution
- **Requirement 3.4**: Action failure handling with clear error messages

The CRUD operations provide the foundation for the chat assistant's SET_REMINDER action, allowing users to create reminders through natural language queries.

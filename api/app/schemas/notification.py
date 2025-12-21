"""
Pydantic schemas for notification system.

This module defines the request/response schemas for:
- Notifications
- Notification preferences
- Notification history
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.notification import NotificationType, NotificationStatus, NotificationChannel


# Base schemas
class NotificationBase(BaseModel):
    """Base schema for notification data"""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: NotificationType
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[str] = Field(None, max_length=50)
    channel: NotificationChannel = NotificationChannel.in_app
    context_data: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a new notification"""
    user_id: str = Field(..., max_length=50)


class NotificationUpdate(BaseModel):
    """Schema for updating notification status"""
    status: NotificationStatus
    read_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response"""
    id: str
    user_id: str
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# Notification Preferences schemas
class NotificationPreferenceBase(BaseModel):
    """Base schema for notification preferences"""
    notification_type: NotificationType
    email_enabled: bool = True
    in_app_enabled: bool = True
    push_enabled: bool = False


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences"""
    user_id: str = Field(..., max_length=50)


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences"""
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema for notification preference response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferencesResponse(BaseModel):
    """Schema for all user notification preferences"""
    preferences: List[NotificationPreferenceResponse]


# Notification History schemas
class NotificationHistoryBase(BaseModel):
    """Base schema for notification history"""
    channel: NotificationChannel
    status: NotificationStatus
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    external_id: Optional[str] = None


class NotificationHistoryCreate(NotificationHistoryBase):
    """Schema for creating notification history entry"""
    notification_id: str = Field(..., max_length=50)


class NotificationHistoryResponse(NotificationHistoryBase):
    """Schema for notification history response"""
    id: str
    notification_id: str
    attempted_at: datetime
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Bulk notification schemas
class BulkNotificationRequest(BaseModel):
    """Schema for sending bulk notifications"""
    user_ids: List[str] = Field(..., min_items=1)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: NotificationType
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[str] = Field(None, max_length=50)
    channel: NotificationChannel = NotificationChannel.in_app
    context_data: Optional[Dict[str, Any]] = None

    @validator('user_ids')
    def validate_user_ids(cls, v):
        if len(v) > 100:  # Limit bulk notifications to 100 users
            raise ValueError('Cannot send bulk notifications to more than 100 users at once')
        return v


class BulkNotificationResponse(BaseModel):
    """Schema for bulk notification response"""
    total_requested: int
    successful: int
    failed: int
    notification_ids: List[str]
    errors: List[Dict[str, str]] = []


# Assignment notification specific schemas
class AssignmentNotificationContext(BaseModel):
    """Context data for assignment notifications"""
    assignment_id: str
    entity_type: str
    entity_id: str
    entity_title: Optional[str] = None
    assigned_by: str
    assigned_by_name: Optional[str] = None
    assignment_type: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None


class TeamNotificationContext(BaseModel):
    """Context data for team notifications"""
    team_id: str
    team_name: str
    project_id: str
    project_name: Optional[str] = None
    action_by: str
    action_by_name: Optional[str] = None
    role: Optional[str] = None


# Notification summary schemas
class NotificationSummary(BaseModel):
    """Schema for notification summary/counts"""
    total_unread: int
    unread_by_type: Dict[NotificationType, int]
    recent_notifications: List[NotificationResponse]


# Email notification schemas
class EmailNotificationData(BaseModel):
    """Schema for email notification data"""
    to_email: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None


# Push notification schemas
class PushNotificationData(BaseModel):
    """Schema for push notification data"""
    user_id: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    badge_count: Optional[int] = None
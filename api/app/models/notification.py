"""
Notification models for the Worky API.

This module defines the database models for:
- User notifications
- Notification preferences
- Notification history
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import enum

from app.db.base import Base


class NotificationType(str, enum.Enum):
    """Types of notifications that can be sent"""
    assignment_created = "assignment_created"
    assignment_removed = "assignment_removed"
    team_member_added = "team_member_added"
    team_member_removed = "team_member_removed"
    assignment_conflict = "assignment_conflict"
    bulk_assignment_completed = "bulk_assignment_completed"
    bulk_assignment_failed = "bulk_assignment_failed"


class NotificationStatus(str, enum.Enum):
    """Status of a notification"""
    pending = "pending"
    sent = "sent"
    failed = "failed"
    read = "read"


class NotificationChannel(str, enum.Enum):
    """Channels through which notifications can be sent"""
    email = "email"
    in_app = "in_app"
    push = "push"


class Notification(Base):
    """
    Model for storing user notifications.
    
    Tracks all notifications sent to users including:
    - Assignment notifications
    - Team membership changes
    - System alerts
    """
    __tablename__ = "notifications"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('NOTIF', 'notifications_id_seq')"))
    
    # Recipient information
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Notification content
    type = Column(ENUM(NotificationType, name='notification_type'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related entity information
    entity_type = Column(String(50))  # 'assignment', 'team', 'project', etc.
    entity_id = Column(String(20))
    
    # Notification metadata
    status = Column(ENUM(NotificationStatus, name='notification_status'), default=NotificationStatus.pending, nullable=False)
    channel = Column(ENUM(NotificationChannel, name='notification_channel'), default=NotificationChannel.in_app, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # Audit fields
    created_by = Column(String(20), ForeignKey("users.id"))
    
    # Additional context data (JSON)
    context_data = Column(Text)  # JSON string for additional context
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes for performance
    __table_args__ = (
        Index('idx_notifications_user_status', 'user_id', 'status'),
        Index('idx_notifications_user_created', 'user_id', 'created_at'),
        Index('idx_notifications_entity', 'entity_type', 'entity_id'),
        Index('idx_notifications_type_status', 'type', 'status'),
    )


class NotificationPreference(Base):
    """
    Model for storing user notification preferences.
    
    Allows users to configure which types of notifications
    they want to receive and through which channels.
    """
    __tablename__ = "notification_preferences"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('NPREF', 'notification_preferences_id_seq')"))
    
    # User and notification type
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(ENUM(NotificationType, name='notification_type'), nullable=False)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True, nullable=False)
    in_app_enabled = Column(Boolean, default=True, nullable=False)
    push_enabled = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")

    # Unique constraint on user_id and notification_type
    __table_args__ = (
        Index('idx_notification_preferences_user_type', 'user_id', 'notification_type', unique=True),
    )


class NotificationHistory(Base):
    """
    Model for tracking notification delivery history.
    
    Maintains a record of all notification attempts including
    success/failure status and delivery details.
    """
    __tablename__ = "notification_history"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('NHIST', 'notification_history_id_seq')"))
    
    # Reference to original notification
    notification_id = Column(String(20), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    
    # Delivery attempt information
    channel = Column(ENUM(NotificationChannel, name='notification_channel'), nullable=False)
    status = Column(ENUM(NotificationStatus, name='notification_status'), nullable=False)
    
    # Delivery details
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivered_at = Column(DateTime(timezone=True))
    
    # Error information (if delivery failed)
    error_message = Column(Text)
    error_code = Column(String(50))
    
    # External service information
    external_id = Column(String(255))  # ID from email service, push service, etc.
    
    # Relationships
    notification = relationship("Notification", back_populates="delivery_history")

    # Indexes for performance
    __table_args__ = (
        Index('idx_notification_history_notification', 'notification_id'),
        Index('idx_notification_history_status', 'status', 'attempted_at'),
    )


# Update Notification model to include delivery_history relationship
Notification.delivery_history = relationship("NotificationHistory", back_populates="notification")


# Add relationships to existing User model
# This would be added to the User model in user.py
"""
# Add these relationships to the User model:

notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user")
notification_preferences = relationship("NotificationPreference", back_populates="user")
"""
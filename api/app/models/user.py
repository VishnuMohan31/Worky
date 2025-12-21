from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('USR', 'users_id_seq')"))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # Keep for backward compatibility
    primary_role = Column(String(50), default="Developer")  # New primary role field
    secondary_roles = Column(ARRAY(String), default=[])  # Array of additional roles
    is_contact_person = Column(Boolean, default=False)  # Flag for client contact person
    client_id = Column(String(20), ForeignKey("clients.id"), nullable=False)
    language = Column(String(10), default="en")
    theme = Column(String(50), default="snow")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="users")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to")
    reported_bugs = relationship("Bug", back_populates="reporter", foreign_keys="Bug.reported_by")
    todo_items = relationship("TodoItem", back_populates="user")
    adhoc_notes = relationship("AdhocNote", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    chat_audit_logs = relationship("ChatAuditLog", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user")
    notification_preferences = relationship("NotificationPreference", back_populates="user")

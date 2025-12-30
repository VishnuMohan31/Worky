from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class ChatMessage(Base):
    """Model for storing chat messages in conversations"""
    __tablename__ = "chat_messages"

    id = Column(String(20), primary_key=True, server_default=func.generate_string_id('MSG', 'chat_messages_id_seq'))
    session_id = Column(String(50), nullable=False, index=True)
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    intent_type = Column(String(50))
    entities = Column(JSON)
    actions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="chat_messages")


class ChatAuditLog(Base):
    """Model for auditing all chat interactions for compliance"""
    __tablename__ = "chat_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(50), nullable=False, unique=True, index=True)
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String(20), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    query = Column(Text, nullable=False)  # PII masked
    intent_type = Column(String(50))
    entities_accessed = Column(JSON)
    action_performed = Column(String(100))
    action_result = Column(String(20))  # "success", "failed", "denied"
    response_summary = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Relationships
    user = relationship("User", back_populates="chat_audit_logs")
    client = relationship("Client", back_populates="chat_audit_logs")


class Reminder(Base):
    """Model for storing user reminders created via chat or UI"""
    __tablename__ = "reminders"

    id = Column(String(20), primary_key=True, server_default=func.generate_string_id('REM', 'reminders_id_seq'))
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # "task", "bug", "project"
    entity_id = Column(String(20), nullable=False)
    message = Column(Text)
    remind_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_sent = Column(Boolean, default=False, index=True)
    created_via = Column(String(20), default="chat")  # "chat", "ui", "api"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="reminders")

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    short_description = Column(String(500))
    long_description = Column(Text)
    email = Column(String(255))
    phone = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(20))
    updated_by = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="client")
    programs = relationship("Program", back_populates="client", cascade="all, delete-orphan")
    chat_audit_logs = relationship("ChatAuditLog", back_populates="client")

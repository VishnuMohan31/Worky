from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Bug(Base):
    __tablename__ = "bugs"

    id = Column(String(20), primary_key=True, default=uuid.uuid4)
    user_story_id = Column(String(20), ForeignKey("user_stories.id"))
    task_id = Column(String(20), ForeignKey("tasks.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    status = Column(String(50), default="New")
    assigned_to = Column(String(20), ForeignKey("users.id"))
    reported_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    environment = Column(String(100))
    steps_to_reproduce = Column(Text)
    expected_behavior = Column(Text)
    actual_behavior = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    # Relationships
    user_story = relationship("UserStory", back_populates="bugs")
    task = relationship("Task", back_populates="bugs")
    assignee = relationship("User", foreign_keys=[assigned_to])
    reporter = relationship("User", back_populates="reported_bugs", foreign_keys=[reported_by])

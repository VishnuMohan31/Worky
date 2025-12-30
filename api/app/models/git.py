from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Commit(Base):
    __tablename__ = "commits"

    id = Column(String(20), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(20), ForeignKey("tasks.id"))
    repository = Column(String(255), nullable=False)
    commit_hash = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    author_email = Column(String(255))
    message = Column(Text, nullable=False)
    committed_at = Column(DateTime(timezone=True), nullable=False)
    branch = Column(String(255))
    url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="commits")


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(String(20), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(20), ForeignKey("tasks.id"))
    repository = Column(String(255), nullable=False)
    pr_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    author = Column(String(255), nullable=False)
    status = Column(String(50), default="open")
    merged_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    task = relationship("Task")

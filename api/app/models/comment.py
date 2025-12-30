from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class BugComment(Base):
    """Comments on bugs"""
    __tablename__ = "bug_comments"
    
    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    bug_id = Column(String(20), ForeignKey("bugs.id"), nullable=False)
    
    # Comment details
    comment_text = Column(Text, nullable=False)
    author_id = Column(String(20), ForeignKey("users.id"), nullable=False)
    
    # Mentions
    mentioned_users = Column(Text)  # JSON array of user IDs
    
    # Edit tracking
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True))
    
    # Attachments
    attachments = Column(Text)  # JSON array of file paths
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    bug = relationship("Bug", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])


class TestCaseComment(Base):
    """Comments on test cases"""
    __tablename__ = "test_case_comments"
    
    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    test_case_id = Column(String(20), ForeignKey("test_cases.id"), nullable=False)
    
    # Comment details
    comment_text = Column(Text, nullable=False)
    author_id = Column(String(20), ForeignKey("users.id"), nullable=False)
    
    # Mentions
    mentioned_users = Column(Text)  # JSON array of user IDs
    
    # Edit tracking
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True))
    
    # Attachments
    attachments = Column(Text)  # JSON array of file paths
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    test_case = relationship("TestCase", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])


class BugAttachment(Base):
    """Attachments for bugs"""
    __tablename__ = "bug_attachments"
    
    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    bug_id = Column(String(20), ForeignKey("bugs.id"), nullable=False)
    
    # File details
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # image/png, application/pdf, etc.
    file_size = Column(Integer)  # in bytes
    
    # Audit fields
    uploaded_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    bug = relationship("Bug", back_populates="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])


class BugStatusHistory(Base):
    """Bug status change history for audit trail"""
    __tablename__ = "bug_status_history"
    
    id = Column(String(20), primary_key=True, default=lambda: str(uuid.uuid4())[:20])
    bug_id = Column(String(20), ForeignKey("bugs.id"), nullable=False)
    
    # Status change
    from_status = Column(String(50))
    to_status = Column(String(50), nullable=False)
    resolution_type = Column(String(50))
    notes = Column(Text)
    
    # Audit fields
    changed_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bug = relationship("Bug", back_populates="status_history")
    changer = relationship("User", foreign_keys=[changed_by])

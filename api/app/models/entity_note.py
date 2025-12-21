from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class EntityNote(Base):
    __tablename__ = "entity_notes"

    id = Column(String(20), primary_key=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(20), nullable=False)
    note_text = Column(Text, nullable=False)
    created_by = Column(String(20), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Decision tracking fields
    is_decision = Column(Boolean, default=False, nullable=False)
    decision_status = Column(String(20), default='Active', nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

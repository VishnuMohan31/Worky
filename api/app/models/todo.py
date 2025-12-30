from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Date, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(String(20), primary_key=True, server_default=func.generate_string_id('TODO', 'todo_items_id_seq'))
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_date = Column(Date, nullable=False)
    visibility = Column(String(10), nullable=False)
    linked_entity_type = Column(String(20))
    linked_entity_id = Column(String(20))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="todo_items")

    # Constraints
    __table_args__ = (
        CheckConstraint("visibility IN ('public', 'private')", name="check_visibility"),
        CheckConstraint("linked_entity_type IN ('task', 'subtask') OR linked_entity_type IS NULL", name="check_entity_type"),
    )


class AdhocNote(Base):
    __tablename__ = "adhoc_notes"

    id = Column(String(20), primary_key=True, server_default=func.generate_string_id('NOTE', 'adhoc_notes_id_seq'))
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    position = Column(Integer, nullable=False, default=0)
    color = Column(String(7), default="#FFEB3B")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="adhoc_notes")

    # Constraints
    __table_args__ = (
        CheckConstraint("position >= 0", name="check_position_positive"),
    )

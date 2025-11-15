from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(String(20), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(20), nullable=False)
    depends_on_type = Column(String(50), nullable=False)
    depends_on_id = Column(String(20), nullable=False)
    dependency_type = Column(String(50), default="finish_to_start")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

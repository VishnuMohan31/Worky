from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(20), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(20), ForeignKey("users.id"))
    client_id = Column(String(20), ForeignKey("clients.id"))
    project_id = Column(String(20), ForeignKey("projects.id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(20), nullable=False)
    changes = Column(JSONB)
    request_id = Column(String(100))
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

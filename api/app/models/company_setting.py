from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CompanySetting(Base):
    __tablename__ = "company_settings"

    id = Column(String(20), primary_key=True)
    client_id = Column(String(20), ForeignKey("clients.id"), nullable=False, unique=True)
    company_name = Column(String(255), nullable=False)
    company_logo_url = Column(String(500))
    company_logo_data = Column(Text)
    primary_color = Column(String(7), default="#4A90E2")
    secondary_color = Column(String(7), default="#2C3E50")
    report_header_text = Column(Text)
    report_footer_text = Column(Text)
    timezone = Column(String(50), default="UTC")
    date_format = Column(String(20), default="YYYY-MM-DD")
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(20), ForeignKey("users.id"))
    updated_by = Column(String(20), ForeignKey("users.id"))

    # Relationships
    client = relationship("Client", back_populates="company_settings")

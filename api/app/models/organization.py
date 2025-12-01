from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    logo_url = Column(String(500))
    logo_data = Column(Text)  # Base64 encoded logo
    description = Column(Text)
    website = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(20))
    updated_by = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships can be added here if needed
    # For example, if organizations are linked to clients:
    # clients = relationship("Client", back_populates="organization")


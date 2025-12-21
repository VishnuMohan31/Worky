"""
Audit Log schemas for the Worky API.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema for audit log responses."""
    
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    changes: Optional[Dict[str, Any]] = None
    created_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogList(BaseModel):
    """Schema for paginated list of audit logs."""
    
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
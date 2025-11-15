from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class EntityNoteCreate(BaseModel):
    note_text: str = Field(..., min_length=1, description="Note content")
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


class EntityNoteResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    note_text: str
    created_by: str
    created_at: datetime
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None

    class Config:
        from_attributes = True

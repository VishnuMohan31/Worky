from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class EntityNoteCreate(BaseModel):
    note_text: str = Field(..., min_length=1, description="Note content")
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    is_decision: Optional[bool] = Field(default=False, description="Flag to mark this note as a decision")
    decision_status: Optional[Literal['Active', 'Canceled', 'Postponed', 'On-Hold', 'Closed']] = Field(
        default='Active', 
        description="Status of the decision if this is a decision note"
    )


class EntityNoteUpdate(BaseModel):
    decision_status: Literal['Active', 'Canceled', 'Postponed', 'On-Hold', 'Closed'] = Field(
        ..., 
        description="New status for the decision"
    )


class EntityNoteResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    note_text: str
    created_by: str
    created_at: datetime
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None
    is_decision: bool = False
    decision_status: Optional[str] = None

    class Config:
        from_attributes = True


class DecisionSummary(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    entity_name: Optional[str] = None
    note_text: str
    decision_status: str
    created_by: str
    created_at: datetime
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True

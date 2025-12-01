from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# Enums
# ============================================================================

class IntentType(str, Enum):
    """Types of user intents in chat queries"""
    QUERY = "query"  # Information retrieval
    ACTION = "action"  # Perform operation
    NAVIGATION = "navigation"  # Request deep link
    REPORT = "report"  # Generate insights
    CLARIFICATION = "clarification"  # Follow-up or ambiguous query


class ActionType(str, Enum):
    """Types of actions that can be performed via chat"""
    VIEW_ENTITY = "view_entity"  # Generate deep link to entity
    SET_REMINDER = "set_reminder"  # Create reminder for task/bug
    UPDATE_STATUS = "update_status"  # Change task/bug status
    CREATE_COMMENT = "create_comment"  # Add comment to entity
    LINK_COMMIT = "link_commit"  # Associate PR/commit with task
    SUGGEST_REPORT = "suggest_report"  # Generate report link


class EntityType(str, Enum):
    """Types of entities in the Worky system"""
    PROJECT = "project"
    TASK = "task"
    SUBTASK = "subtask"
    USER_STORY = "user_story"
    USECASE = "usecase"
    BUG = "bug"
    PROGRAM = "program"
    TEST_CASE = "test_case"
    USER = "user"


class ActionResult(str, Enum):
    """Result status of an action execution"""
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"


# ============================================================================
# Entity Extraction
# ============================================================================

class ExtractedEntity(BaseModel):
    """Represents an extracted entity from user query"""
    entity_type: EntityType
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    confidence: float = 1.0


# ============================================================================
# Session Data Structures
# ============================================================================

class SessionEntity(BaseModel):
    """Entity reference stored in session context"""
    entity_type: EntityType
    entity_id: str
    entity_name: Optional[str] = None


class SessionContext(BaseModel):
    """Conversation context stored in Redis session"""
    session_id: str
    user_id: str
    client_id: str
    current_project: Optional[str] = None
    mentioned_entities: List[SessionEntity] = Field(default_factory=list)
    last_intent: Optional[IntentType] = None
    created_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Chat Request/Response Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Schema for incoming chat query requests"""
    query: str = Field(..., min_length=1, max_length=2000, description="User's natural language query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context data")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query is not empty after stripping whitespace"""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: Optional[str]) -> Optional[str]:
        """Generate session ID if not provided"""
        if v is None:
            return str(uuid.uuid4())
        return v


class UIAction(BaseModel):
    """UI action metadata for rich responses"""
    action_type: ActionType
    label: str
    entity_type: Optional[EntityType] = None
    entity_id: Optional[str] = None
    deep_link: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EntityCard(BaseModel):
    """Structured entity data for card display"""
    entity_type: EntityType
    entity_id: str
    title: str
    status: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    deep_link: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DataTable(BaseModel):
    """Tabular data for list display"""
    columns: List[str]
    rows: List[List[Any]]
    total_count: int
    has_more: bool = False


class ChatMetadata(BaseModel):
    """Metadata about the chat response"""
    request_id: str
    intent_type: Optional[IntentType] = None
    entities_accessed: List[str] = Field(default_factory=list)
    response_time_ms: Optional[int] = None
    llm_tokens_used: Optional[int] = None


class ChatResponse(BaseModel):
    """Schema for chat response"""
    status: Literal["success", "error"] = "success"
    message: str = Field(..., description="Human-readable response text")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured data")
    cards: Optional[List[EntityCard]] = Field(default_factory=list, description="Entity cards for display")
    table: Optional[DataTable] = None
    actions: Optional[List[UIAction]] = Field(default_factory=list, description="Available UI actions")
    metadata: Optional[ChatMetadata] = None

    class Config:
        from_attributes = True


class ChatErrorResponse(BaseModel):
    """Schema for chat error responses"""
    status: Literal["error"] = "error"
    error: Dict[str, Any] = Field(..., description="Error details")

    class Config:
        from_attributes = True


# ============================================================================
# Chat Message Schemas
# ============================================================================

class ChatMessageBase(BaseModel):
    """Base schema for chat messages"""
    role: Literal["user", "assistant"]
    content: str


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    session_id: str
    user_id: str
    intent_type: Optional[IntentType] = None
    entities: Optional[Dict[str, Any]] = Field(default_factory=dict)
    actions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message responses"""
    id: str
    session_id: str
    user_id: str
    intent_type: Optional[IntentType] = None
    entities: Optional[Dict[str, Any]] = Field(default_factory=dict)
    actions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history retrieval"""
    messages: List[ChatMessageResponse]
    session_metadata: Optional[SessionContext] = None
    total: int


# ============================================================================
# Reminder Schemas
# ============================================================================

class ReminderBase(BaseModel):
    """Base schema for reminders"""
    entity_type: Literal["task", "bug", "project"]
    entity_id: str = Field(..., max_length=20)
    message: Optional[str] = Field(None, max_length=500)
    remind_at: datetime


class ReminderCreate(ReminderBase):
    """Schema for creating a reminder"""
    created_via: Literal["chat", "ui", "api"] = "chat"

    @field_validator("remind_at")
    @classmethod
    def validate_remind_at(cls, v: datetime) -> datetime:
        """Validate reminder is in the future"""
        if v <= datetime.now(v.tzinfo):
            raise ValueError("Reminder time must be in the future")
        return v


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder"""
    message: Optional[str] = Field(None, max_length=500)
    remind_at: Optional[datetime] = None
    is_sent: Optional[bool] = None

    @field_validator("remind_at")
    @classmethod
    def validate_remind_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate reminder is in the future if provided"""
        if v is not None and v <= datetime.now(v.tzinfo):
            raise ValueError("Reminder time must be in the future")
        return v


class ReminderResponse(ReminderBase):
    """Schema for reminder responses"""
    id: str
    user_id: str
    is_sent: bool
    created_via: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReminderList(BaseModel):
    """Schema for paginated list of reminders"""
    reminders: List[ReminderResponse]
    total: int


# ============================================================================
# Audit Log Schemas
# ============================================================================

class ChatAuditLogCreate(BaseModel):
    """Schema for creating a chat audit log entry"""
    request_id: str
    user_id: str
    client_id: str
    session_id: str
    query: str  # Should be PII masked before storage
    intent_type: Optional[IntentType] = None
    entities_accessed: Optional[List[str]] = Field(default_factory=list)
    action_performed: Optional[str] = None
    action_result: Optional[ActionResult] = None
    response_summary: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ChatAuditLogResponse(BaseModel):
    """Schema for chat audit log responses"""
    id: uuid.UUID
    request_id: str
    user_id: str
    client_id: str
    session_id: str
    query: str
    intent_type: Optional[str] = None
    entities_accessed: Optional[List[str]] = Field(default_factory=list)
    action_performed: Optional[str] = None
    action_result: Optional[str] = None
    response_summary: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class ChatAuditLogList(BaseModel):
    """Schema for paginated list of audit logs"""
    logs: List[ChatAuditLogResponse]
    total: int


# ============================================================================
# Health Check Schema
# ============================================================================

class ChatHealthResponse(BaseModel):
    """Schema for chat service health check"""
    status: Literal["healthy", "degraded", "unhealthy"]
    llm_available: bool
    db_available: bool
    redis_available: bool
    timestamp: datetime

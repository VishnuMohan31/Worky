"""
Tests for Session Service.

These tests validate the core functionality of the SessionService including:
- Session creation and retrieval
- Conversation context storage
- Entity resolution from conversation history
- Session expiration and cleanup
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.session_service import SessionService, get_session_service
from app.schemas.chat import (
    SessionContext,
    SessionEntity,
    ChatMessageResponse,
    IntentType,
    EntityType
)


@pytest.fixture
def session_service():
    """Create a SessionService instance with mocked Redis"""
    service = SessionService()
    service.redis_client = AsyncMock()
    return service


@pytest.fixture
def sample_session_id():
    """Generate a sample session ID"""
    return str(uuid4())


@pytest.fixture
def sample_user_id():
    """Generate a sample user ID"""
    return "USR-001"


@pytest.fixture
def sample_client_id():
    """Generate a sample client ID"""
    return "CLI-001"


@pytest.fixture
def sample_session_context(sample_session_id, sample_user_id, sample_client_id):
    """Create a sample session context"""
    return SessionContext(
        session_id=sample_session_id,
        user_id=sample_user_id,
        client_id=sample_client_id,
        current_project="PRJ-001",
        mentioned_entities=[
            SessionEntity(
                entity_type=EntityType.TASK,
                entity_id="TSK-001",
                entity_name="Sample Task"
            )
        ],
        last_intent=IntentType.QUERY,
        created_at=datetime.utcnow(),
        last_activity=datetime.utcnow()
    )


@pytest.fixture
def sample_message(sample_session_id, sample_user_id):
    """Create a sample chat message"""
    return ChatMessageResponse(
        id="MSG-001",
        session_id=sample_session_id,
        user_id=sample_user_id,
        role="user",
        content="Show me tasks for Project X",
        intent_type=IntentType.QUERY,
        entities={"project": "PRJ-001"},
        actions=[],
        created_at=datetime.utcnow()
    )


@pytest.mark.asyncio
async def test_create_session(session_service, sample_session_id, sample_user_id, sample_client_id):
    """Test session creation"""
    # Mock Redis setex
    session_service.redis_client.setex = AsyncMock(return_value=True)
    
    # Create session
    session_context = await session_service.create_session(
        session_id=sample_session_id,
        user_id=sample_user_id,
        client_id=sample_client_id,
        current_project="PRJ-001"
    )
    
    # Verify session context
    assert session_context.session_id == sample_session_id
    assert session_context.user_id == sample_user_id
    assert session_context.client_id == sample_client_id
    assert session_context.current_project == "PRJ-001"
    assert session_context.mentioned_entities == []
    assert session_context.last_intent is None
    
    # Verify Redis was called
    session_service.redis_client.setex.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_found(session_service, sample_session_id, sample_session_context):
    """Test retrieving an existing session"""
    # Mock Redis get to return session data
    import json
    session_data = sample_session_context.model_dump(mode='json')
    session_data['created_at'] = session_data['created_at'].isoformat()
    session_data['last_activity'] = session_data['last_activity'].isoformat()
    
    session_service.redis_client.get = AsyncMock(return_value=json.dumps(session_data))
    
    # Get session
    retrieved_session = await session_service.get_session(sample_session_id)
    
    # Verify session was retrieved
    assert retrieved_session is not None
    assert retrieved_session.session_id == sample_session_context.session_id
    assert retrieved_session.user_id == sample_session_context.user_id
    assert retrieved_session.client_id == sample_session_context.client_id


@pytest.mark.asyncio
async def test_get_session_not_found(session_service, sample_session_id):
    """Test retrieving a non-existent session"""
    # Mock Redis get to return None
    session_service.redis_client.get = AsyncMock(return_value=None)
    
    # Get session
    retrieved_session = await session_service.get_session(sample_session_id)
    
    # Verify session was not found
    assert retrieved_session is None


@pytest.mark.asyncio
async def test_store_message(session_service, sample_session_id, sample_message):
    """Test storing a message in conversation history"""
    # Mock Redis operations
    session_service.redis_client.rpush = AsyncMock(return_value=1)
    session_service.redis_client.ltrim = AsyncMock(return_value=True)
    session_service.redis_client.expire = AsyncMock(return_value=True)
    
    # Store message
    result = await session_service.store_message(sample_session_id, sample_message)
    
    # Verify message was stored
    assert result is True
    session_service.redis_client.rpush.assert_called_once()
    session_service.redis_client.ltrim.assert_called_once()
    session_service.redis_client.expire.assert_called_once()


@pytest.mark.asyncio
async def test_get_conversation_history(session_service, sample_session_id, sample_message):
    """Test retrieving conversation history"""
    # Mock Redis lrange to return message data
    import json
    message_data = sample_message.model_dump(mode='json')
    message_data['created_at'] = message_data['created_at'].isoformat()
    
    session_service.redis_client.lrange = AsyncMock(return_value=[json.dumps(message_data)])
    
    # Get conversation history
    messages = await session_service.get_conversation_history(sample_session_id)
    
    # Verify messages were retrieved
    assert len(messages) == 1
    assert messages[0].id == sample_message.id
    assert messages[0].content == sample_message.content


@pytest.mark.asyncio
async def test_resolve_entity_from_context(session_service, sample_session_id, sample_session_context):
    """Test entity resolution from conversation context"""
    # Mock get_session to return context with entities
    with patch.object(session_service, 'get_session', return_value=sample_session_context):
        # Resolve "it" reference
        entity = await session_service.resolve_entity_from_context(sample_session_id, "it")
        
        # Verify entity was resolved
        assert entity is not None
        assert entity.entity_type == EntityType.TASK
        assert entity.entity_id == "TSK-001"


@pytest.mark.asyncio
async def test_resolve_entity_type_specific(session_service, sample_session_id):
    """Test type-specific entity resolution"""
    # Create context with multiple entity types
    context = SessionContext(
        session_id=sample_session_id,
        user_id="USR-001",
        client_id="CLI-001",
        mentioned_entities=[
            SessionEntity(entity_type=EntityType.PROJECT, entity_id="PRJ-001", entity_name="Project A"),
            SessionEntity(entity_type=EntityType.TASK, entity_id="TSK-001", entity_name="Task 1"),
            SessionEntity(entity_type=EntityType.BUG, entity_id="BUG-001", entity_name="Bug 1"),
        ],
        created_at=datetime.utcnow(),
        last_activity=datetime.utcnow()
    )
    
    with patch.object(session_service, 'get_session', return_value=context):
        # Resolve "that task"
        entity = await session_service.resolve_entity_from_context(sample_session_id, "that task")
        
        # Verify correct entity type was resolved
        assert entity is not None
        assert entity.entity_type == EntityType.TASK
        assert entity.entity_id == "TSK-001"


@pytest.mark.asyncio
async def test_delete_session(session_service, sample_session_id):
    """Test session deletion"""
    # Mock Redis delete
    session_service.redis_client.delete = AsyncMock(return_value=2)
    
    # Delete session
    result = await session_service.delete_session(sample_session_id)
    
    # Verify session was deleted
    assert result is True
    session_service.redis_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_update_session(session_service, sample_session_id, sample_session_context):
    """Test session update"""
    # Mock get_session and setex
    with patch.object(session_service, 'get_session', return_value=sample_session_context):
        session_service.redis_client.setex = AsyncMock(return_value=True)
        
        # Update session with new intent
        new_entity = SessionEntity(
            entity_type=EntityType.BUG,
            entity_id="BUG-001",
            entity_name="New Bug"
        )
        
        result = await session_service.update_session(
            session_id=sample_session_id,
            last_intent=IntentType.ACTION,
            new_entities=[new_entity]
        )
        
        # Verify update was successful
        assert result is True
        session_service.redis_client.setex.assert_called_once()


@pytest.mark.asyncio
async def test_extend_session_ttl(session_service, sample_session_id):
    """Test extending session TTL"""
    # Mock Redis expire
    session_service.redis_client.expire = AsyncMock(return_value=True)
    
    # Extend TTL
    result = await session_service.extend_session_ttl(sample_session_id)
    
    # Verify TTL was extended
    assert result is True
    assert session_service.redis_client.expire.call_count == 2  # Called for both session and messages keys


def test_get_session_service_singleton():
    """Test that get_session_service returns a singleton"""
    service1 = get_session_service()
    service2 = get_session_service()
    
    # Verify same instance is returned
    assert service1 is service2

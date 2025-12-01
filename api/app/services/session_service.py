"""
Session Management Service for Chat Assistant

This service manages conversation sessions using Redis for storage.
It handles session creation, retrieval, context storage, and entity resolution.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.core.config import settings
from app.schemas.chat import (
    SessionContext,
    SessionEntity,
    ChatMessageResponse,
    IntentType,
    EntityType
)
from app.services.chat_metrics import get_chat_metrics

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing chat sessions with Redis"""
    
    def __init__(self):
        """Initialize Redis connection pool"""
        self.redis_client: Optional[aioredis.Redis] = None
        self.session_ttl = timedelta(minutes=settings.CHAT_SESSION_TTL_MINUTES)
        self.max_context_messages = settings.CHAT_MAX_CONTEXT_MESSAGES
        self.metrics = get_chat_metrics()
    
    async def connect(self) -> None:
        """Establish Redis connection"""
        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established for session service")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    def _get_session_key(self, session_id: str) -> str:
        """Generate Redis key for session data"""
        return f"chat:session:{session_id}"
    
    def _get_messages_key(self, session_id: str) -> str:
        """Generate Redis key for session messages"""
        return f"chat:messages:{session_id}"
    
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        client_id: str,
        current_project: Optional[str] = None
    ) -> SessionContext:
        """
        Create a new chat session
        
        Args:
            session_id: Unique session identifier
            user_id: User ID
            client_id: Client ID for RBAC
            current_project: Optional current project context
            
        Returns:
            SessionContext object
            
        Raises:
            RedisError: If Redis operation fails
        """
        if not self.redis_client:
            await self.connect()
        
        now = datetime.utcnow()
        session_context = SessionContext(
            session_id=session_id,
            user_id=user_id,
            client_id=client_id,
            current_project=current_project,
            mentioned_entities=[],
            last_intent=None,
            created_at=now,
            last_activity=now
        )
        
        try:
            session_key = self._get_session_key(session_id)
            session_data = session_context.model_dump(mode='json')
            
            # Convert datetime objects to ISO format strings
            session_data['created_at'] = session_data['created_at'].isoformat()
            session_data['last_activity'] = session_data['last_activity'].isoformat()
            
            # Store session with TTL
            await self.redis_client.setex(
                session_key,
                int(self.session_ttl.total_seconds()),
                json.dumps(session_data)
            )
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_context
            
        except RedisError as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve session context from Redis
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionContext if found, None otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            session_key = self._get_session_key(session_id)
            session_data = await self.redis_client.get(session_key)
            
            if not session_data:
                logger.debug(f"Session {session_id} not found or expired")
                return None
            
            # Parse JSON and reconstruct SessionContext
            data = json.loads(session_data)
            
            # Convert ISO format strings back to datetime
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            data['last_activity'] = datetime.fromisoformat(data['last_activity'])
            
            # Convert mentioned_entities list to SessionEntity objects
            if 'mentioned_entities' in data:
                data['mentioned_entities'] = [
                    SessionEntity(**entity) for entity in data['mentioned_entities']
                ]
            
            session_context = SessionContext(**data)
            logger.debug(f"Retrieved session {session_id}")
            return session_context
            
        except (RedisError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to retrieve session {session_id}: {e}")
            return None
    
    async def update_session(
        self,
        session_id: str,
        last_intent: Optional[IntentType] = None,
        current_project: Optional[str] = None,
        new_entities: Optional[List[SessionEntity]] = None
    ) -> bool:
        """
        Update session context with new information
        
        Args:
            session_id: Session identifier
            last_intent: Latest intent type
            current_project: Updated current project
            new_entities: New entities to add to context
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            session_context = await self.get_session(session_id)
            if not session_context:
                logger.warning(f"Cannot update non-existent session {session_id}")
                return False
            
            # Update fields
            if last_intent:
                session_context.last_intent = last_intent
            
            if current_project:
                session_context.current_project = current_project
            
            if new_entities:
                # Add new entities, avoiding duplicates
                existing_ids = {
                    (e.entity_type, e.entity_id) 
                    for e in session_context.mentioned_entities
                }
                for entity in new_entities:
                    if (entity.entity_type, entity.entity_id) not in existing_ids:
                        session_context.mentioned_entities.append(entity)
            
            # Update last activity timestamp
            session_context.last_activity = datetime.utcnow()
            
            # Save updated session
            session_key = self._get_session_key(session_id)
            session_data = session_context.model_dump(mode='json')
            
            # Convert datetime objects to ISO format strings
            session_data['created_at'] = session_data['created_at'].isoformat()
            session_data['last_activity'] = session_data['last_activity'].isoformat()
            
            await self.redis_client.setex(
                session_key,
                int(self.session_ttl.total_seconds()),
                json.dumps(session_data)
            )
            
            logger.debug(f"Updated session {session_id}")
            return True
            
        except RedisError as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    async def store_message(
        self,
        session_id: str,
        message: ChatMessageResponse
    ) -> bool:
        """
        Store a message in the session's conversation history
        
        Args:
            session_id: Session identifier
            message: Chat message to store
            
        Returns:
            True if storage successful, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            messages_key = self._get_messages_key(session_id)
            
            # Convert message to JSON
            message_data = message.model_dump(mode='json')
            message_data['created_at'] = message_data['created_at'].isoformat()
            
            # Add message to list (right push)
            await self.redis_client.rpush(messages_key, json.dumps(message_data))
            
            # Trim list to keep only last N messages
            await self.redis_client.ltrim(
                messages_key,
                -self.max_context_messages,
                -1
            )
            
            # Set TTL on messages list
            await self.redis_client.expire(
                messages_key,
                int(self.session_ttl.total_seconds())
            )
            
            logger.debug(f"Stored message in session {session_id}")
            return True
            
        except RedisError as e:
            logger.error(f"Failed to store message in session {session_id}: {e}")
            return False
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[ChatMessageResponse]:
        """
        Retrieve conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve (default: max_context_messages)
            
        Returns:
            List of ChatMessageResponse objects
        """
        if not self.redis_client:
            await self.connect()
        
        if limit is None:
            limit = self.max_context_messages
        
        try:
            messages_key = self._get_messages_key(session_id)
            
            # Get last N messages
            messages_data = await self.redis_client.lrange(
                messages_key,
                -limit,
                -1
            )
            
            if not messages_data:
                logger.debug(f"No conversation history for session {session_id}")
                return []
            
            # Parse messages
            messages = []
            for msg_json in messages_data:
                try:
                    msg_data = json.loads(msg_json)
                    msg_data['created_at'] = datetime.fromisoformat(msg_data['created_at'])
                    messages.append(ChatMessageResponse(**msg_data))
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse message in session {session_id}: {e}")
                    continue
            
            logger.debug(f"Retrieved {len(messages)} messages for session {session_id}")
            return messages
            
        except RedisError as e:
            logger.error(f"Failed to retrieve conversation history for session {session_id}: {e}")
            return []
    
    async def resolve_entity_from_context(
        self,
        session_id: str,
        entity_reference: str
    ) -> Optional[SessionEntity]:
        """
        Resolve entity reference from conversation context
        
        This handles pronouns and references like "it", "that task", "the bug"
        by looking at recently mentioned entities in the session.
        
        Args:
            session_id: Session identifier
            entity_reference: Reference to resolve (e.g., "it", "that task")
            
        Returns:
            SessionEntity if resolved, None otherwise
        """
        session_context = await self.get_session(session_id)
        if not session_context or not session_context.mentioned_entities:
            return None
        
        # Normalize reference
        ref_lower = entity_reference.lower().strip()
        
        # Simple resolution: return most recent entity
        if ref_lower in ["it", "this", "that"]:
            return session_context.mentioned_entities[-1] if session_context.mentioned_entities else None
        
        # Type-specific resolution
        entity_type_map = {
            "task": EntityType.TASK,
            "bug": EntityType.BUG,
            "project": EntityType.PROJECT,
            "story": EntityType.USER_STORY,
            "usecase": EntityType.USECASE,
            "subtask": EntityType.SUBTASK,
        }
        
        for keyword, entity_type in entity_type_map.items():
            if keyword in ref_lower:
                # Find most recent entity of this type
                for entity in reversed(session_context.mentioned_entities):
                    if entity.entity_type == entity_type:
                        return entity
        
        return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its conversation history
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            session_key = self._get_session_key(session_id)
            messages_key = self._get_messages_key(session_id)
            
            # Delete both keys
            deleted = await self.redis_client.delete(session_key, messages_key)
            
            if deleted > 0:
                logger.info(f"Deleted session {session_id}")
                return True
            else:
                logger.debug(f"Session {session_id} not found for deletion")
                return False
                
        except RedisError as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (Redis handles TTL automatically)
        
        This method is primarily for monitoring and logging purposes,
        as Redis automatically removes expired keys.
        
        Returns:
            Number of active sessions
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            # Count active sessions
            pattern = "chat:session:*"
            cursor = 0
            active_count = 0
            
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                active_count += len(keys)
                
                if cursor == 0:
                    break
            
            logger.info(f"Active sessions: {active_count}")
            
            # Update metrics
            self.metrics.set_active_sessions(active_count)
            
            return active_count
            
        except RedisError as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    async def extend_session_ttl(self, session_id: str) -> bool:
        """
        Extend the TTL of an active session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if TTL extended, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            session_key = self._get_session_key(session_id)
            messages_key = self._get_messages_key(session_id)
            
            # Extend TTL for both keys
            ttl_seconds = int(self.session_ttl.total_seconds())
            await self.redis_client.expire(session_key, ttl_seconds)
            await self.redis_client.expire(messages_key, ttl_seconds)
            
            logger.debug(f"Extended TTL for session {session_id}")
            return True
            
        except RedisError as e:
            logger.error(f"Failed to extend TTL for session {session_id}: {e}")
            return False


# Singleton instance
_session_service: Optional[SessionService] = None


def get_session_service() -> SessionService:
    """Get or create the session service singleton"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service

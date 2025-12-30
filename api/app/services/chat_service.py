"""
Chat Service Orchestrator

This is the main orchestrator that integrates all chat assistant services:
- Session management
- Intent classification
- Data retrieval with RBAC
- LLM response generation
- Action execution
- Audit logging

It implements the end-to-end query processing flow with error handling
and response formatting.
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    IntentType,
    ActionType,
    ActionResult,
    ChatAuditLogCreate,
    UIAction
)
from app.services.session_service import get_session_service
from app.services.intent_classifier import get_intent_classifier
from app.services.data_retriever import get_data_retriever
from app.services.llm_service import get_llm_service
from app.services.action_handler import get_action_handler, ActionExecutionError
from app.services.audit_service import get_audit_service
from app.services.chat_metrics import get_chat_metrics
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChatService:
    """Main orchestrator for chat assistant functionality"""
    
    def __init__(self):
        """Initialize chat service with all dependencies"""
        self.session_service = get_session_service()
        self.intent_classifier = get_intent_classifier()
        self.data_retriever = get_data_retriever()
        self.llm_service = get_llm_service()
        self.action_handler = get_action_handler()
        self.audit_service = get_audit_service()
        self.metrics = get_chat_metrics()
        
        # Set LLM service for intent classifier fallback
        self.intent_classifier.set_llm_service(self.llm_service)
    
    async def initialize(self) -> None:
        """Initialize all services"""
        try:
            await self.session_service.connect()
            await self.llm_service.connect()
            logger.info("Chat service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chat service: {e}")
            raise
    
    async def process_query(
        self,
        db: AsyncSession,
        user: User,
        request: ChatRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a chat query end-to-end
        
        Args:
            db: Database session
            user: Current user
            request: Chat request with query and session_id
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            ChatResponse with message, data, and actions
        """
        # Generate request ID for tracking
        request_id = f"req_{uuid.uuid4().hex[:16]}"
        start_time = datetime.utcnow()
        
        logger.info(
            f"Processing chat query: request_id={request_id}, "
            f"user_id={user.id}, session_id={request.session_id}"
        )
        
        # Track request duration
        with self.metrics.track_request_duration():
            try:
                # Step 1: Get or create session
                session = await self._get_or_create_session(
                    user, request.session_id, request.context
                )
                
                # Step 2: Classify intent and extract entities
                intent = await self.intent_classifier.classify_with_llm_fallback(
                    request.query,
                    context={
                        'last_intent': session.last_intent,
                        'mentioned_entities': [
                            {'type': e.entity_type.value, 'id': e.entity_id}
                            for e in session.mentioned_entities
                        ]
                    }
                )
                
                logger.debug(
                    f"Intent classified: type={intent.intent_type.value}, "
                    f"confidence={intent.confidence:.2f}, entities={len(intent.entities)}"
                )
                
                # Step 3: Handle based on intent type
                if intent.intent_type == IntentType.ACTION:
                    response = await self._handle_action_intent(
                        db, user, request, intent, request_id
                    )
                elif intent.intent_type == IntentType.NAVIGATION:
                    response = await self._handle_navigation_intent(
                        db, user, request, intent, request_id
                    )
                elif intent.intent_type == IntentType.CLARIFICATION:
                    response = await self._handle_clarification_intent(
                        db, user, request, intent, session, request_id
                    )
                else:
                    # QUERY or REPORT intent
                    response = await self._handle_query_intent(
                        db, user, request, intent, session, request_id
                    )
                
                # Step 4: Update session with new context
                await self._update_session_context(
                    session.session_id,
                    intent,
                    response
                )
                
                # Step 5: Store message in conversation history
                await self._store_message(session.session_id, user, request.query, response)
                
                # Step 6: Create audit log
                await self._create_audit_log(
                    user,
                    session.session_id,
                    request.query,
                    intent,
                    response,
                    request_id,
                    ip_address,
                    user_agent
                )
                
                # Calculate processing time
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Record successful request metric
                self.metrics.record_request(
                    intent_type=intent.intent_type.value,
                    status="success"
                )
                
                logger.info(
                    f"Query processed successfully: request_id={request_id}, "
                    f"duration_ms={duration_ms}, intent={intent.intent_type.value}"
                )
                
                return response
            
            except ActionExecutionError as e:
                # Handle action execution errors
                logger.warning(f"Action execution error: {e.message}")
                
                # Record error metric
                self.metrics.record_error("action_failed")
                self.metrics.record_request(
                    intent_type="action",
                    status="error"
                )
                
                error_response = ChatResponse(
                    status="error",
                    message=e.message,
                    data={},
                    actions=[],
                    metadata={
                        "request_id": request_id,
                        "error_code": "ACTION_FAILED",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Still audit the failed action
                await self._create_audit_log(
                    user,
                    request.session_id,
                    request.query,
                    None,
                    error_response,
                    request_id,
                    ip_address,
                    user_agent,
                    action_result=e.result
                )
                
                return error_response
            
            except Exception as e:
                logger.error(f"Error processing query: {e}", exc_info=True)
                
                # Record error metric
                self.metrics.record_error("internal")
                self.metrics.record_request(
                    intent_type="unknown",
                    status="error"
                )
                
                error_response = ChatResponse(
                    status="error",
                    message="I encountered an error processing your request. Please try again.",
                    data={},
                    actions=[],
                    metadata={
                        "request_id": request_id,
                        "error_code": "INTERNAL_ERROR",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Audit the error
                await self._create_audit_log(
                    user,
                    request.session_id,
                    request.query,
                    None,
                    error_response,
                    request_id,
                    ip_address,
                    user_agent,
                    action_result=ActionResult.FAILED
                )
                
                return error_response
    
    async def _get_or_create_session(
        self,
        user: User,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Get existing session or create new one"""
        session = await self.session_service.get_session(session_id)
        
        if not session:
            # Create new session
            current_project = context.get('current_project') if context else None
            session = await self.session_service.create_session(
                session_id=session_id,
                user_id=user.id,
                client_id=user.client_id,
                current_project=current_project
            )
            logger.info(f"Created new session: {session_id}")
        else:
            # Extend TTL for existing session
            await self.session_service.extend_session_ttl(session_id)
        
        return session
    
    async def _handle_query_intent(
        self,
        db: AsyncSession,
        user: User,
        request: ChatRequest,
        intent,
        session,
        request_id: str
    ) -> ChatResponse:
        """Handle QUERY or REPORT intent"""
        # Step 1: Retrieve data based on intent and entities
        retrieved_data = await self._retrieve_data(db, user, intent)
        
        logger.debug(f"Retrieved data keys: {list(retrieved_data.keys())}")
        
        # Step 2: Generate LLM response
        conversation_history = await self.session_service.get_conversation_history(
            session.session_id,
            limit=3
        )
        
        conversation_context = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history
        ]
        
        response_text, tokens_used = await self.llm_service.generate_response(
            query=request.query,
            retrieved_data=retrieved_data,
            intent_type=intent.intent_type,
            conversation_context=conversation_context
        )
        
        # Step 3: Parse structured output
        structured_output = self.llm_service.parse_structured_output(
            response_text,
            retrieved_data
        )
        
        # Step 4: Build response
        return ChatResponse(
            status="success",
            message=structured_output.get("text", response_text),
            data=retrieved_data,
            actions=self._format_ui_actions(structured_output.get("actions", [])),
            metadata={
                "request_id": request_id,
                "intent_type": intent.intent_type.value,
                "confidence": intent.confidence,
                "tokens_used": tokens_used,
                "entities_found": len(intent.entities),
                "timestamp": datetime.utcnow().isoformat(),
                "cards": structured_output.get("cards", []),
                "table": structured_output.get("table")
            }
        )
    
    async def _handle_action_intent(
        self,
        db: AsyncSession,
        user: User,
        request: ChatRequest,
        intent,
        request_id: str
    ) -> ChatResponse:
        """Handle ACTION intent"""
        # Extract action parameters from query
        action_params = self.intent_classifier.extract_action_parameters(
            request.query,
            intent
        )
        
        if not action_params or 'action_type' not in action_params:
            return ChatResponse(
                status="error",
                message="I couldn't determine what action you want to perform. "
                        "Please be more specific (e.g., 'set reminder for TSK-123 tomorrow').",
                data={},
                actions=[],
                metadata={
                    "request_id": request_id,
                    "error_code": "AMBIGUOUS_ACTION",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Get action type
        action_type_str = action_params.pop('action_type')
        try:
            action_type = ActionType(action_type_str.lower())
        except ValueError:
            action_type = ActionType.VIEW_ENTITY
        
        # Add entity information from intent
        if intent.entities:
            entity = intent.entities[0]
            action_params['entity_type'] = entity.entity_type.value
            action_params['entity_id'] = entity.entity_id or entity.entity_name
        
        # Execute action
        action_result = await self.action_handler.execute_action(
            db=db,
            user=user,
            action_type=action_type,
            parameters=action_params
        )
        
        # Build response
        return ChatResponse(
            status="success",
            message=action_result.get('message', 'Action completed successfully'),
            data=action_result,
            actions=[],
            metadata={
                "request_id": request_id,
                "intent_type": intent.intent_type.value,
                "action_type": action_type.value,
                "action_result": action_result.get('result', 'success'),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def _handle_navigation_intent(
        self,
        db: AsyncSession,
        user: User,
        request: ChatRequest,
        intent,
        request_id: str
    ) -> ChatResponse:
        """Handle NAVIGATION intent"""
        if not intent.entities:
            return ChatResponse(
                status="error",
                message="I couldn't identify which item you want to view. "
                        "Please specify an ID (e.g., 'open TSK-123').",
                data={},
                actions=[],
                metadata={
                    "request_id": request_id,
                    "error_code": "NO_ENTITY",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Get first entity
        entity = intent.entities[0]
        
        # Execute VIEW_ENTITY action
        action_result = await self.action_handler.execute_action(
            db=db,
            user=user,
            action_type=ActionType.VIEW_ENTITY,
            parameters={
                'entity_type': entity.entity_type.value,
                'entity_id': entity.entity_id or entity.entity_name
            }
        )
        
        # Build response with deep link
        return ChatResponse(
            status="success",
            message=action_result.get('message', 'Here\'s the link'),
            data=action_result,
            actions=[
                UIAction(
                    action_type=ActionType.VIEW_ENTITY,
                    label=f"Open {entity.entity_type.value.title()}",
                    entity_type=entity.entity_type,
                    entity_id=entity.entity_id,
                    deep_link=action_result.get('deep_link'),
                    parameters={}
                )
            ],
            metadata={
                "request_id": request_id,
                "intent_type": intent.intent_type.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def _handle_clarification_intent(
        self,
        db: AsyncSession,
        user: User,
        request: ChatRequest,
        intent,
        session,
        request_id: str
    ) -> ChatResponse:
        """Handle CLARIFICATION intent"""
        # Get recent conversation history
        conversation_history = await self.session_service.get_conversation_history(
            session.session_id,
            limit=5
        )
        
        if not conversation_history:
            return ChatResponse(
                status="success",
                message="I'm here to help! You can ask me about tasks, projects, bugs, "
                        "or request actions like setting reminders or updating status.",
                data={},
                actions=[],
                metadata={
                    "request_id": request_id,
                    "intent_type": intent.intent_type.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Use LLM to generate clarification response based on context
        conversation_context = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history
        ]
        
        response_text, tokens_used = await self.llm_service.generate_response(
            query=request.query,
            retrieved_data={},
            intent_type=intent.intent_type,
            conversation_context=conversation_context
        )
        
        return ChatResponse(
            status="success",
            message=response_text,
            data={},
            actions=[],
            metadata={
                "request_id": request_id,
                "intent_type": intent.intent_type.value,
                "tokens_used": tokens_used,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def _retrieve_data(
        self,
        db: AsyncSession,
        user: User,
        intent
    ) -> Dict[str, Any]:
        """Retrieve data based on intent and entities"""
        retrieved_data = {}
        
        try:
            # Resolve entities to database objects
            if intent.entities:
                resolved = await self.data_retriever.resolve_entities(
                    db, user, intent.entities
                )
                
                # Convert resolved entities to serializable format
                for key, entities in resolved.items():
                    retrieved_data[key] = [
                        self._serialize_entity(entity) for entity in entities
                    ]
            
            # Handle REPORT intent - get aggregate data
            if intent.intent_type == IntentType.REPORT:
                # Determine what kind of report
                query_lower = intent.normalized_query.lower()
                
                if any(word in query_lower for word in ['task', 'tasks']):
                    stats = await self.data_retriever.get_task_statistics(
                        db, user,
                        start_date=intent.temporal_context.get('start_date'),
                        end_date=intent.temporal_context.get('end_date')
                    )
                    retrieved_data['task_statistics'] = stats
                
                elif any(word in query_lower for word in ['bug', 'bugs']):
                    stats = await self.data_retriever.get_bug_statistics(
                        db, user,
                        start_date=intent.temporal_context.get('start_date'),
                        end_date=intent.temporal_context.get('end_date')
                    )
                    retrieved_data['bug_statistics'] = stats
                
                elif any(word in query_lower for word in ['project', 'projects']):
                    stats = await self.data_retriever.get_project_statistics(db, user)
                    retrieved_data['project_statistics'] = stats
                
                elif any(word in query_lower for word in ['workload', 'assigned', 'my']):
                    stats = await self.data_retriever.get_user_workload(db, user)
                    retrieved_data['user_workload'] = stats
            
            # Handle QUERY intent - get filtered data
            elif intent.intent_type == IntentType.QUERY:
                # Apply temporal filters if present
                filters = {}
                if intent.temporal_context:
                    if 'status_filter' in intent.temporal_context:
                        filters['status'] = intent.temporal_context['status_filter']
                    if 'priority_filter' in intent.temporal_context:
                        filters['priority'] = intent.temporal_context['priority_filter']
                    if 'start_date' in intent.temporal_context:
                        filters['start_date'] = intent.temporal_context['start_date']
                    if 'end_date' in intent.temporal_context:
                        filters['end_date'] = intent.temporal_context['end_date']
                
                # Determine what to query based on keywords
                query_lower = intent.normalized_query.lower()
                
                if any(word in query_lower for word in ['task', 'tasks']):
                    tasks = await self.data_retriever.get_tasks_by_filters(
                        db, user, **filters
                    )
                    retrieved_data['tasks'] = [
                        self._serialize_entity(task) for task in tasks
                    ]
                
                elif any(word in query_lower for word in ['bug', 'bugs', 'issue', 'issues']):
                    bugs = await self.data_retriever.get_bugs_by_filters(
                        db, user, **filters
                    )
                    retrieved_data['bugs'] = [
                        self._serialize_entity(bug) for bug in bugs
                    ]
                
                elif any(word in query_lower for word in ['project', 'projects']):
                    projects = await self.data_retriever.get_projects_by_filters(
                        db, user, **filters
                    )
                    retrieved_data['projects'] = [
                        self._serialize_entity(project) for project in projects
                    ]
                
                elif any(word in query_lower for word in ['story', 'stories', 'user story']):
                    stories = await self.data_retriever.get_user_stories_by_filters(
                        db, user, **filters
                    )
                    retrieved_data['user_stories'] = [
                        self._serialize_entity(story) for story in stories
                    ]
            
            logger.debug(f"Retrieved data: {len(retrieved_data)} categories")
            
        except Exception as e:
            logger.error(f"Error retrieving data: {e}", exc_info=True)
            # Return empty data on error
        
        return retrieved_data
    
    def _serialize_entity(self, entity: Any) -> Dict[str, Any]:
        """Serialize database entity to dictionary"""
        if hasattr(entity, '__dict__'):
            # Get all non-private attributes
            data = {
                key: value
                for key, value in entity.__dict__.items()
                if not key.startswith('_')
            }
            
            # Convert datetime objects to ISO format
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
            
            return data
        
        return {}
    
    def _format_ui_actions(self, actions: List[Dict[str, Any]]) -> List[UIAction]:
        """Format actions as UIAction objects"""
        ui_actions = []
        
        for action in actions:
            try:
                ui_action = UIAction(
                    action_type=ActionType(action.get('action_type', 'view_entity')),
                    label=action.get('label', 'View'),
                    entity_type=action.get('entity_type'),
                    entity_id=action.get('entity_id'),
                    deep_link=action.get('deep_link'),
                    parameters=action.get('parameters', {})
                )
                ui_actions.append(ui_action)
            except Exception as e:
                logger.warning(f"Failed to format UI action: {e}")
                continue
        
        return ui_actions
    
    async def _update_session_context(
        self,
        session_id: str,
        intent,
        response: ChatResponse
    ) -> None:
        """Update session with new context"""
        try:
            # Extract new entities from intent
            from app.schemas.chat import SessionEntity
            
            new_entities = []
            for entity in intent.entities:
                if entity.entity_id:
                    new_entities.append(SessionEntity(
                        entity_type=entity.entity_type,
                        entity_id=entity.entity_id,
                        entity_name=entity.entity_name
                    ))
            
            # Update session
            await self.session_service.update_session(
                session_id=session_id,
                last_intent=intent.intent_type,
                new_entities=new_entities if new_entities else None
            )
            
        except Exception as e:
            logger.warning(f"Failed to update session context: {e}")
    
    async def _store_message(
        self,
        session_id: str,
        user: User,
        query: str,
        response: ChatResponse
    ) -> None:
        """Store message in conversation history"""
        try:
            # Store user message
            user_message = ChatMessageResponse(
                id=f"msg_{uuid.uuid4().hex[:16]}",
                session_id=session_id,
                role="user",
                content=query,
                intent_type=None,
                entities=[],
                actions=[],
                created_at=datetime.utcnow()
            )
            
            await self.session_service.store_message(session_id, user_message)
            
            # Store assistant message
            assistant_message = ChatMessageResponse(
                id=f"msg_{uuid.uuid4().hex[:16]}",
                session_id=session_id,
                role="assistant",
                content=response.message,
                intent_type=response.metadata.get('intent_type'),
                entities=[],
                actions=response.actions,
                created_at=datetime.utcnow()
            )
            
            await self.session_service.store_message(session_id, assistant_message)
            
        except Exception as e:
            logger.warning(f"Failed to store message: {e}")
    
    async def _create_audit_log(
        self,
        user: User,
        session_id: str,
        query: str,
        intent,
        response: ChatResponse,
        request_id: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        action_result: Optional[ActionResult] = None
    ) -> None:
        """Create audit log entry"""
        try:
            # Extract entities accessed
            entities_accessed = []
            if intent and intent.entities:
                entities_accessed = [
                    f"{e.entity_type.value}:{e.entity_id or e.entity_name}"
                    for e in intent.entities
                ]
            
            # Determine action performed
            action_performed = None
            if response.metadata.get('action_type'):
                action_performed = response.metadata['action_type']
            
            # Determine action result
            if action_result is None:
                if response.status == "success":
                    action_result = ActionResult.SUCCESS
                else:
                    action_result = ActionResult.FAILED
            
            # Create audit log
            audit_data = ChatAuditLogCreate(
                request_id=request_id,
                user_id=user.id,
                client_id=user.client_id,
                session_id=session_id,
                query=query,
                intent_type=intent.intent_type if intent else None,
                entities_accessed=entities_accessed,
                action_performed=action_performed,
                action_result=action_result,
                response_summary=response.message[:500] if response.message else None,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Use batch logging if enabled
            use_batch = settings.CHAT_ENABLE_AUDIT_LOGGING
            
            # Note: We need a database session here, but for now we'll skip
            # actual creation since we don't have db in this context
            # This would be handled by the endpoint layer
            logger.debug(f"Audit log prepared: {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[ChatMessageResponse]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages
            
        Returns:
            List of chat messages
        """
        try:
            messages = await self.session_service.get_conversation_history(
                session_id,
                limit=limit
            )
            return messages
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its conversation history
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted successfully
        """
        try:
            return await self.session_service.delete_session(session_id)
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of all services
        
        Returns:
            Dictionary with health status
        """
        health = {
            "status": "healthy",
            "services": {}
        }
        
        # Check LLM service
        try:
            llm_healthy = await self.llm_service.health_check()
            health["services"]["llm"] = "healthy" if llm_healthy else "unhealthy"
        except Exception as e:
            health["services"]["llm"] = "unhealthy"
            logger.warning(f"LLM health check failed: {e}")
        
        # Check Redis (session service)
        try:
            if self.session_service.redis_client:
                await self.session_service.redis_client.ping()
                health["services"]["redis"] = "healthy"
                
                # Update active sessions metric
                active_sessions = await self.session_service.cleanup_expired_sessions()
                health["active_sessions"] = active_sessions
            else:
                health["services"]["redis"] = "not_connected"
        except Exception as e:
            health["services"]["redis"] = "unhealthy"
            logger.warning(f"Redis health check failed: {e}")
        
        # Overall status
        if any(status == "unhealthy" for status in health["services"].values()):
            health["status"] = "degraded"
        
        return health


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create the chat service singleton"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service

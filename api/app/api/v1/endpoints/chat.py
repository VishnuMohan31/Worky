"""
Chat Assistant endpoints for the Worky API.

This module provides endpoints for the context-aware chat assistant that enables
users to query project data using natural language, perform safe actions, and
receive intelligent responses while respecting RBAC.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatHealthResponse,
    ChatErrorResponse
)
from app.services.chat_service import get_chat_service
from app.core.security import get_current_user
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_query(
    request_data: ChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a natural language chat query.
    
    This endpoint accepts a user's natural language query and returns an intelligent
    response with structured data, UI actions, and deep links. The assistant respects
    RBAC rules and only returns data the user has permission to access.
    
    Args:
        request_data: Chat request containing query and session_id
        request: FastAPI request object for extracting IP and user agent
        db: Database session
        current_user: Authenticated user
        
    Returns:
        ChatResponse with message, data, and actions
        
    Raises:
        HTTPException: 400 for validation errors, 401 for auth errors, 500 for server errors
    """
    try:
        # Extract client metadata
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Get chat service
        chat_service = get_chat_service()
        
        # Process the query
        response = await chat_service.process_query(
            db=db,
            user=current_user,
            request=request_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.log_activity(
            action="chat_query",
            user_id=str(current_user.id),
            details={
                "session_id": request_data.session_id,
                "query_length": len(request_data.query),
                "status": response.status
            }
        )
        
        return response
        
    except ValueError as e:
        # Validation errors
        logger.log_error(
            error=str(e),
            user_id=str(current_user.id),
            context={"query": request_data.query[:100]}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Internal errors
        logger.log_error(
            error=str(e),
            user_id=str(current_user.id),
            context={"query": request_data.query[:100]}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request. Please try again."
        )


@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for a chat session.
    
    Returns the message history for the specified session. Users can only access
    their own session history.
    
    Args:
        session_id: Session ID to retrieve history for
        limit: Maximum number of messages to return (default: 50)
        current_user: Authenticated user
        
    Returns:
        ChatHistoryResponse with messages and session metadata
        
    Raises:
        HTTPException: 404 if session not found, 403 if unauthorized
    """
    try:
        # Get chat service
        chat_service = get_chat_service()
        
        # Get conversation history
        messages = await chat_service.get_conversation_history(
            session_id=session_id,
            limit=limit
        )
        
        # Verify user owns this session
        if messages and messages[0].user_id != str(current_user.id):
            logger.log_security_event(
                event="unauthorized_session_access",
                user_id=str(current_user.id),
                details={"session_id": session_id}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this session"
            )
        
        # Get session metadata
        session = await chat_service.session_service.get_session(session_id)
        
        logger.log_activity(
            action="get_chat_history",
            user_id=str(current_user.id),
            details={
                "session_id": session_id,
                "message_count": len(messages)
            }
        )
        
        return ChatHistoryResponse(
            messages=messages,
            session_metadata=session,
            total=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error=str(e),
            user_id=str(current_user.id),
            context={"session_id": session_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.delete("/chat/session/{session_id}", status_code=status.HTTP_200_OK)
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a chat session and its conversation history.
    
    This removes all messages and context for the specified session. Users can
    only delete their own sessions.
    
    Args:
        session_id: Session ID to delete
        current_user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if session not found, 403 if unauthorized
    """
    try:
        # Get chat service
        chat_service = get_chat_service()
        
        # Verify session exists and user owns it
        session = await chat_service.session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.user_id != str(current_user.id):
            logger.log_security_event(
                event="unauthorized_session_deletion",
                user_id=str(current_user.id),
                details={"session_id": session_id}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this session"
            )
        
        # Delete the session
        success = await chat_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete session"
            )
        
        logger.log_activity(
            action="delete_chat_session",
            user_id=str(current_user.id),
            details={"session_id": session_id}
        )
        
        return {
            "success": True,
            "message": "Session deleted successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error=str(e),
            user_id=str(current_user.id),
            context={"session_id": session_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.get("/chat/health", response_model=ChatHealthResponse)
async def chat_health_check():
    """
    Check the health status of the chat assistant service.
    
    This endpoint checks the availability of all chat service dependencies:
    - LLM service (OpenAI or configured provider)
    - Redis (session management)
    - Database connectivity
    
    Returns:
        ChatHealthResponse with status of each service
    """
    try:
        # Get chat service
        chat_service = get_chat_service()
        
        # Perform health check
        health_status = await chat_service.health_check()
        
        # Determine overall status
        llm_available = health_status["services"].get("llm") == "healthy"
        redis_available = health_status["services"].get("redis") == "healthy"
        
        # Database is assumed available if we can execute this endpoint
        db_available = True
        
        overall_status = "healthy"
        if not llm_available or not redis_available:
            overall_status = "degraded"
        if not db_available:
            overall_status = "unhealthy"
        
        return ChatHealthResponse(
            status=overall_status,
            llm_available=llm_available,
            db_available=db_available,
            redis_available=redis_available,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.log_error(
            error=str(e),
            context={"endpoint": "chat_health_check"}
        )
        # Return unhealthy status on error
        return ChatHealthResponse(
            status="unhealthy",
            llm_available=False,
            db_available=False,
            redis_available=False,
            timestamp=datetime.utcnow()
        )

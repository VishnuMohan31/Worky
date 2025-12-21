"""
Audit Log endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import datetime

from app.db.base import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogResponse, AuditLogList
from app.core.security import get_current_user
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/{entity_type}/{entity_id}", response_model=AuditLogList)
async def get_audit_logs(
    entity_type: str = Path(..., description="Entity type (task, subtask, project, etc.)"),
    entity_id: str = Path(..., description="Entity ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs for a specific entity."""
    
    # Build query
    query = select(AuditLog).where(
        and_(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        )
    )
    
    # Apply filters
    if action:
        query = query.where(AuditLog.action == action)
    
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.where(AuditLog.created_at >= from_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            # Set to end of day
            to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.where(AuditLog.created_at <= to_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    # Get total count
    count_query = select(AuditLog).where(
        and_(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        )
    )
    if action:
        count_query = count_query.where(AuditLog.action == action)
    if date_from:
        count_query = count_query.where(AuditLog.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        to_date = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59, microsecond=999999)
        count_query = count_query.where(AuditLog.created_at <= to_date)
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply pagination and ordering
    query = query.order_by(desc(AuditLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    audit_logs = result.scalars().all()
    
    # Convert to response format
    items = []
    for log in audit_logs:
        # Get user name if available
        user_name = None
        if log.user_id:
            user_result = await db.execute(select(User).where(User.id == log.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user_name = user.full_name or user.email
        
        items.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_name=user_name,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            changes=log.changes,
            created_at=log.created_at,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent
        ))
    
    logger.log_activity(
        action="view_audit_logs",
        entity_type=entity_type,
        entity_id=entity_id,
        filters={
            "action": action,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "page_size": page_size
        }
    )
    
    return AuditLogList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get("/", response_model=AuditLogList)
async def list_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all audit logs with optional filters (Admin only)."""
    
    # Only admins can view all audit logs
    if current_user.role != "Admin":
        raise AccessDeniedException("Only administrators can view all audit logs")
    
    # Build query
    query = select(AuditLog)
    
    # Apply filters
    filters = []
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)
    if user_id:
        filters.append(AuditLog.user_id == user_id)
    if action:
        filters.append(AuditLog.action == action)
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            filters.append(AuditLog.created_at >= from_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            filters.append(AuditLog.created_at <= to_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    if filters:
        query = query.where(and_(*filters))
    
    # Get total count
    count_query = select(AuditLog)
    if filters:
        count_query = count_query.where(and_(*filters))
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply pagination and ordering
    query = query.order_by(desc(AuditLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    audit_logs = result.scalars().all()
    
    # Convert to response format
    items = []
    for log in audit_logs:
        # Get user name if available
        user_name = None
        if log.user_id:
            user_result = await db.execute(select(User).where(User.id == log.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user_name = user.full_name or user.email
        
        items.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_name=user_name,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            changes=log.changes,
            created_at=log.created_at,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent
        ))
    
    logger.log_activity(
        action="list_audit_logs",
        filters={
            "entity_type": entity_type,
            "user_id": user_id,
            "action": action,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "page_size": page_size
        }
    )
    
    return AuditLogList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )
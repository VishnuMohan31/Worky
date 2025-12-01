"""
Audit Logging Service for Chat Assistant

This service handles audit logging for all chat interactions with PII masking,
batch logging for performance, and querying capabilities for admin dashboards.
"""

import logging
import re
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.chat import ChatAuditLog
from app.schemas.chat import (
    ChatAuditLogCreate,
    ChatAuditLogResponse,
    ChatAuditLogList,
    IntentType,
    ActionResult
)

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging with PII masking and batch operations"""
    
    # PII patterns for masking
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
    
    # Name patterns (common titles + capitalized words)
    NAME_PATTERN = re.compile(
        r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    )
    
    def __init__(self):
        """Initialize audit service"""
        self._batch_queue: List[ChatAuditLogCreate] = []
        self._batch_size = 10
        self._batch_timeout = 5.0  # seconds
        self._batch_lock = asyncio.Lock()
        self._batch_task: Optional[asyncio.Task] = None
    
    def mask_pii(self, text: str) -> str:
        """
        Mask personally identifiable information in text
        
        Args:
            text: Text that may contain PII
            
        Returns:
            Text with PII masked
        """
        if not text:
            return text
        
        masked = text
        
        # Mask emails
        masked = self.EMAIL_PATTERN.sub('[EMAIL]', masked)
        
        # Mask credit card numbers (before phone to avoid conflicts)
        masked = self.CREDIT_CARD_PATTERN.sub('[CREDIT_CARD]', masked)
        
        # Mask SSN
        masked = self.SSN_PATTERN.sub('[SSN]', masked)
        
        # Mask phone numbers
        masked = self.PHONE_PATTERN.sub('[PHONE]', masked)
        
        # Mask names with titles
        masked = self.NAME_PATTERN.sub('[NAME]', masked)
        
        return masked
    
    def _truncate_text(self, text: Optional[str], max_length: int = 500) -> Optional[str]:
        """
        Truncate text to maximum length
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text or None
        """
        if not text:
            return text
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."
    
    async def create_audit_log(
        self,
        db: AsyncSession,
        audit_data: ChatAuditLogCreate,
        use_batch: bool = False
    ) -> Optional[ChatAuditLog]:
        """
        Create an audit log entry
        
        Args:
            db: Database session
            audit_data: Audit log data
            use_batch: Whether to use batch logging (default: False)
            
        Returns:
            Created audit log or None if batched
        """
        # Mask PII in query
        masked_query = self.mask_pii(audit_data.query)
        
        # Truncate response summary
        truncated_summary = self._truncate_text(audit_data.response_summary)
        
        # Create audit log data
        log_data = {
            "request_id": audit_data.request_id,
            "user_id": audit_data.user_id,
            "client_id": audit_data.client_id,
            "session_id": audit_data.session_id,
            "query": masked_query,
            "intent_type": audit_data.intent_type.value if audit_data.intent_type else None,
            "entities_accessed": audit_data.entities_accessed or [],
            "action_performed": audit_data.action_performed,
            "action_result": audit_data.action_result.value if audit_data.action_result else None,
            "response_summary": truncated_summary,
            "ip_address": audit_data.ip_address,
            "user_agent": self._truncate_text(audit_data.user_agent, 255)
        }
        
        if use_batch:
            # Add to batch queue
            async with self._batch_lock:
                self._batch_queue.append(audit_data)
                
                # Start batch processor if not running
                if self._batch_task is None or self._batch_task.done():
                    self._batch_task = asyncio.create_task(
                        self._process_batch(db)
                    )
            
            logger.debug(f"Audit log queued for batch processing: {audit_data.request_id}")
            return None
        else:
            # Create immediately
            try:
                audit_log = ChatAuditLog(**log_data)
                db.add(audit_log)
                await db.commit()
                await db.refresh(audit_log)
                
                logger.info(f"Audit log created: {audit_log.request_id}")
                return audit_log
                
            except Exception as e:
                logger.error(f"Failed to create audit log: {e}")
                await db.rollback()
                raise
    
    async def _process_batch(self, db: AsyncSession) -> None:
        """
        Process batch of audit logs
        
        Args:
            db: Database session
        """
        await asyncio.sleep(self._batch_timeout)
        
        async with self._batch_lock:
            if not self._batch_queue:
                return
            
            # Get batch to process
            batch = self._batch_queue[:self._batch_size]
            self._batch_queue = self._batch_queue[self._batch_size:]
        
        try:
            # Create audit logs in batch
            audit_logs = []
            for audit_data in batch:
                masked_query = self.mask_pii(audit_data.query)
                truncated_summary = self._truncate_text(audit_data.response_summary)
                
                log_data = {
                    "request_id": audit_data.request_id,
                    "user_id": audit_data.user_id,
                    "client_id": audit_data.client_id,
                    "session_id": audit_data.session_id,
                    "query": masked_query,
                    "intent_type": audit_data.intent_type.value if audit_data.intent_type else None,
                    "entities_accessed": audit_data.entities_accessed or [],
                    "action_performed": audit_data.action_performed,
                    "action_result": audit_data.action_result.value if audit_data.action_result else None,
                    "response_summary": truncated_summary,
                    "ip_address": audit_data.ip_address,
                    "user_agent": self._truncate_text(audit_data.user_agent, 255)
                }
                
                audit_logs.append(ChatAuditLog(**log_data))
            
            # Bulk insert
            db.add_all(audit_logs)
            await db.commit()
            
            logger.info(f"Batch processed: {len(audit_logs)} audit logs created")
            
        except Exception as e:
            logger.error(f"Failed to process audit log batch: {e}")
            await db.rollback()
            
            # Re-queue failed items
            async with self._batch_lock:
                self._batch_queue.extend(batch)
    
    async def get_audit_logs(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        session_id: Optional[str] = None,
        intent_type: Optional[IntentType] = None,
        action_result: Optional[ActionResult] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> ChatAuditLogList:
        """
        Query audit logs with filters
        
        Args:
            db: Database session
            user_id: Filter by user ID
            client_id: Filter by client ID
            session_id: Filter by session ID
            intent_type: Filter by intent type
            action_result: Filter by action result
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            ChatAuditLogList with logs and total count
        """
        try:
            # Build query
            query = select(ChatAuditLog)
            count_query = select(func.count(ChatAuditLog.id))
            
            # Apply filters
            filters = []
            
            if user_id:
                filters.append(ChatAuditLog.user_id == user_id)
            
            if client_id:
                filters.append(ChatAuditLog.client_id == client_id)
            
            if session_id:
                filters.append(ChatAuditLog.session_id == session_id)
            
            if intent_type:
                filters.append(ChatAuditLog.intent_type == intent_type.value)
            
            if action_result:
                filters.append(ChatAuditLog.action_result == action_result.value)
            
            if start_date:
                filters.append(ChatAuditLog.timestamp >= start_date)
            
            if end_date:
                filters.append(ChatAuditLog.timestamp <= end_date)
            
            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))
            
            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0
            
            # Apply pagination and ordering
            query = query.order_by(ChatAuditLog.timestamp.desc())
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await db.execute(query)
            logs = result.scalars().all()
            
            # Convert to response schema
            log_responses = [
                ChatAuditLogResponse(
                    id=log.id,
                    request_id=log.request_id,
                    user_id=log.user_id,
                    client_id=log.client_id,
                    session_id=log.session_id,
                    query=log.query,
                    intent_type=log.intent_type,
                    entities_accessed=log.entities_accessed or [],
                    action_performed=log.action_performed,
                    action_result=log.action_result,
                    response_summary=log.response_summary,
                    timestamp=log.timestamp,
                    ip_address=log.ip_address,
                    user_agent=log.user_agent
                )
                for log in logs
            ]
            
            logger.debug(f"Retrieved {len(log_responses)} audit logs (total: {total})")
            
            return ChatAuditLogList(
                logs=log_responses,
                total=total
            )
            
        except Exception as e:
            logger.error(f"Failed to query audit logs: {e}")
            raise
    
    async def get_audit_log_by_request_id(
        self,
        db: AsyncSession,
        request_id: str
    ) -> Optional[ChatAuditLogResponse]:
        """
        Get a specific audit log by request ID
        
        Args:
            db: Database session
            request_id: Request ID
            
        Returns:
            ChatAuditLogResponse or None if not found
        """
        try:
            query = select(ChatAuditLog).where(ChatAuditLog.request_id == request_id)
            result = await db.execute(query)
            log = result.scalar_one_or_none()
            
            if not log:
                logger.debug(f"Audit log not found: {request_id}")
                return None
            
            return ChatAuditLogResponse(
                id=log.id,
                request_id=log.request_id,
                user_id=log.user_id,
                client_id=log.client_id,
                session_id=log.session_id,
                query=log.query,
                intent_type=log.intent_type,
                entities_accessed=log.entities_accessed or [],
                action_performed=log.action_performed,
                action_result=log.action_result,
                response_summary=log.response_summary,
                timestamp=log.timestamp,
                ip_address=log.ip_address,
                user_agent=log.user_agent
            )
            
        except Exception as e:
            logger.error(f"Failed to get audit log by request ID: {e}")
            raise
    
    async def get_audit_statistics(
        self,
        db: AsyncSession,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit log statistics for analytics
        
        Args:
            db: Database session
            client_id: Filter by client ID
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Dictionary with statistics
        """
        try:
            # Build base filters
            filters = []
            
            if client_id:
                filters.append(ChatAuditLog.client_id == client_id)
            
            if start_date:
                filters.append(ChatAuditLog.timestamp >= start_date)
            
            if end_date:
                filters.append(ChatAuditLog.timestamp <= end_date)
            
            base_where = and_(*filters) if filters else None
            
            # Total queries
            total_query = select(func.count(ChatAuditLog.id))
            if base_where is not None:
                total_query = total_query.where(base_where)
            
            total_result = await db.execute(total_query)
            total_queries = total_result.scalar() or 0
            
            # Queries by intent type
            intent_query = select(
                ChatAuditLog.intent_type,
                func.count(ChatAuditLog.id).label('count')
            ).group_by(ChatAuditLog.intent_type)
            
            if base_where is not None:
                intent_query = intent_query.where(base_where)
            
            intent_result = await db.execute(intent_query)
            queries_by_intent = {
                row.intent_type or "unknown": row.count
                for row in intent_result
            }
            
            # Actions by result
            action_query = select(
                ChatAuditLog.action_result,
                func.count(ChatAuditLog.id).label('count')
            ).where(ChatAuditLog.action_performed.isnot(None))
            
            if base_where is not None:
                action_query = action_query.where(base_where)
            
            action_query = action_query.group_by(ChatAuditLog.action_result)
            action_result = await db.execute(action_query)
            actions_by_result = {
                row.action_result or "unknown": row.count
                for row in action_result
            }
            
            # Top users
            user_query = select(
                ChatAuditLog.user_id,
                func.count(ChatAuditLog.id).label('count')
            ).group_by(ChatAuditLog.user_id).order_by(func.count(ChatAuditLog.id).desc()).limit(10)
            
            if base_where is not None:
                user_query = user_query.where(base_where)
            
            user_result = await db.execute(user_query)
            top_users = [
                {"user_id": row.user_id, "query_count": row.count}
                for row in user_result
            ]
            
            statistics = {
                "total_queries": total_queries,
                "queries_by_intent": queries_by_intent,
                "actions_by_result": actions_by_result,
                "top_users": top_users,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
            
            logger.debug(f"Retrieved audit statistics: {total_queries} total queries")
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get audit statistics: {e}")
            raise
    
    async def flush_batch(self, db: AsyncSession) -> None:
        """
        Flush any remaining items in the batch queue
        
        Args:
            db: Database session
        """
        async with self._batch_lock:
            if not self._batch_queue:
                return
            
            batch = self._batch_queue.copy()
            self._batch_queue.clear()
        
        try:
            audit_logs = []
            for audit_data in batch:
                masked_query = self.mask_pii(audit_data.query)
                truncated_summary = self._truncate_text(audit_data.response_summary)
                
                log_data = {
                    "request_id": audit_data.request_id,
                    "user_id": audit_data.user_id,
                    "client_id": audit_data.client_id,
                    "session_id": audit_data.session_id,
                    "query": masked_query,
                    "intent_type": audit_data.intent_type.value if audit_data.intent_type else None,
                    "entities_accessed": audit_data.entities_accessed or [],
                    "action_performed": audit_data.action_performed,
                    "action_result": audit_data.action_result.value if audit_data.action_result else None,
                    "response_summary": truncated_summary,
                    "ip_address": audit_data.ip_address,
                    "user_agent": self._truncate_text(audit_data.user_agent, 255)
                }
                
                audit_logs.append(ChatAuditLog(**log_data))
            
            db.add_all(audit_logs)
            await db.commit()
            
            logger.info(f"Flushed batch: {len(audit_logs)} audit logs created")
            
        except Exception as e:
            logger.error(f"Failed to flush audit log batch: {e}")
            await db.rollback()


# Singleton instance
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Get or create the audit service singleton"""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service

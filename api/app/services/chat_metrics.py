"""
Chat Metrics Service

Provides Prometheus metrics for monitoring chat assistant performance and usage.
Tracks request counts, durations, errors, rate limits, and active sessions.
"""

import logging
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)


# Request metrics
chat_requests_total = Counter(
    'chat_requests_total',
    'Total number of chat requests',
    ['intent_type', 'status']
)

# Duration metrics
chat_request_duration_seconds = Histogram(
    'chat_request_duration_seconds',
    'Chat request processing duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0]
)

chat_llm_call_duration_seconds = Histogram(
    'chat_llm_call_duration_seconds',
    'LLM API call duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0]
)

# Error metrics
chat_errors_total = Counter(
    'chat_errors_total',
    'Total number of chat errors',
    ['error_type']
)

# Rate limiting metrics
chat_rate_limit_exceeded_total = Counter(
    'chat_rate_limit_exceeded_total',
    'Total number of rate limit violations',
    ['window_type']
)

# Session metrics
chat_active_sessions = Gauge(
    'chat_active_sessions',
    'Number of active chat sessions'
)

# Action metrics
chat_actions_executed_total = Counter(
    'chat_actions_executed_total',
    'Total number of actions executed',
    ['action_type', 'result']
)


class ChatMetrics:
    """Service for tracking chat assistant metrics"""
    
    @staticmethod
    def record_request(intent_type: str, status: str) -> None:
        """
        Record a chat request
        
        Args:
            intent_type: Type of intent (query, action, navigation, report, clarification)
            status: Request status (success, error)
        """
        try:
            chat_requests_total.labels(
                intent_type=intent_type.lower(),
                status=status.lower()
            ).inc()
        except Exception as e:
            logger.warning(f"Failed to record request metric: {e}")
    
    @staticmethod
    @contextmanager
    def track_request_duration():
        """
        Context manager to track request duration
        
        Usage:
            with ChatMetrics.track_request_duration():
                # process request
                pass
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            try:
                chat_request_duration_seconds.observe(duration)
            except Exception as e:
                logger.warning(f"Failed to record request duration: {e}")
    
    @staticmethod
    @contextmanager
    def track_llm_call_duration():
        """
        Context manager to track LLM call duration
        
        Usage:
            with ChatMetrics.track_llm_call_duration():
                # call LLM
                pass
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            try:
                chat_llm_call_duration_seconds.observe(duration)
            except Exception as e:
                logger.warning(f"Failed to record LLM duration: {e}")
    
    @staticmethod
    def record_error(error_type: str) -> None:
        """
        Record an error
        
        Args:
            error_type: Type of error (validation, authentication, authorization, 
                       llm_timeout, llm_unavailable, database, internal)
        """
        try:
            chat_errors_total.labels(error_type=error_type.lower()).inc()
        except Exception as e:
            logger.warning(f"Failed to record error metric: {e}")
    
    @staticmethod
    def record_rate_limit_exceeded(window_type: str) -> None:
        """
        Record a rate limit violation
        
        Args:
            window_type: Type of rate limit window (minute, hour)
        """
        try:
            chat_rate_limit_exceeded_total.labels(
                window_type=window_type.lower()
            ).inc()
        except Exception as e:
            logger.warning(f"Failed to record rate limit metric: {e}")
    
    @staticmethod
    def set_active_sessions(count: int) -> None:
        """
        Set the number of active sessions
        
        Args:
            count: Number of active sessions
        """
        try:
            chat_active_sessions.set(count)
        except Exception as e:
            logger.warning(f"Failed to set active sessions metric: {e}")
    
    @staticmethod
    def record_action_executed(action_type: str, result: str) -> None:
        """
        Record an action execution
        
        Args:
            action_type: Type of action (view_entity, set_reminder, update_status, 
                        create_comment, link_commit, suggest_report)
            result: Action result (success, failed, denied)
        """
        try:
            chat_actions_executed_total.labels(
                action_type=action_type.lower(),
                result=result.lower()
            ).inc()
        except Exception as e:
            logger.warning(f"Failed to record action metric: {e}")


# Singleton instance
_chat_metrics: Optional[ChatMetrics] = None


def get_chat_metrics() -> ChatMetrics:
    """Get or create the chat metrics singleton"""
    global _chat_metrics
    if _chat_metrics is None:
        _chat_metrics = ChatMetrics()
    return _chat_metrics

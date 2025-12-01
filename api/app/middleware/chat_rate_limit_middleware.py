"""
Chat Rate Limiting Middleware

Implements token bucket algorithm using Redis for rate limiting chat requests.
Enforces per-user limits: 60 req/min, 1000 req/hour with burst allowance.
"""

import time
import logging
from typing import Optional, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import status
from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logging import StructuredLogger
from app.services.chat_metrics import get_chat_metrics

logger = StructuredLogger(__name__)


class TokenBucket:
    """Token bucket implementation for rate limiting"""
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        capacity: int,
        refill_rate: float,
        window_seconds: int
    ):
        """
        Initialize token bucket
        
        Args:
            redis_client: Redis client instance
            capacity: Maximum tokens in bucket (burst allowance)
            refill_rate: Tokens added per second
            window_seconds: Time window for rate calculation
        """
        self.redis = redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.window_seconds = window_seconds
    
    def _get_bucket_key(self, identifier: str, window_type: str) -> str:
        """Generate Redis key for token bucket"""
        return f"chat:ratelimit:{window_type}:{identifier}"
    
    async def consume(
        self,
        identifier: str,
        window_type: str,
        tokens: int = 1
    ) -> Tuple[bool, int, float]:
        """
        Attempt to consume tokens from bucket
        
        Args:
            identifier: User identifier (user_id)
            window_type: "minute" or "hour"
            tokens: Number of tokens to consume
            
        Returns:
            Tuple of (allowed, remaining_tokens, retry_after_seconds)
        """
        bucket_key = self._get_bucket_key(identifier, window_type)
        current_time = time.time()
        
        try:
            # Get current bucket state
            bucket_data = await self.redis.get(bucket_key)
            
            if bucket_data:
                # Parse existing bucket state
                parts = bucket_data.split(":")
                last_tokens = float(parts[0])
                last_update = float(parts[1])
            else:
                # Initialize new bucket
                last_tokens = float(self.capacity)
                last_update = current_time
            
            # Calculate tokens to add based on time elapsed
            time_elapsed = current_time - last_update
            tokens_to_add = time_elapsed * self.refill_rate
            
            # Update token count (capped at capacity)
            current_tokens = min(self.capacity, last_tokens + tokens_to_add)
            
            # Check if we have enough tokens
            if current_tokens >= tokens:
                # Consume tokens
                new_tokens = current_tokens - tokens
                
                # Store updated bucket state
                bucket_value = f"{new_tokens}:{current_time}"
                await self.redis.setex(
                    bucket_key,
                    self.window_seconds,
                    bucket_value
                )
                
                return True, int(new_tokens), 0.0
            else:
                # Not enough tokens - calculate retry after
                tokens_needed = tokens - current_tokens
                retry_after = tokens_needed / self.refill_rate
                
                # Update last check time without consuming
                bucket_value = f"{current_tokens}:{current_time}"
                await self.redis.setex(
                    bucket_key,
                    self.window_seconds,
                    bucket_value
                )
                
                return False, int(current_tokens), retry_after
                
        except RedisError as e:
            logger.error(f"Redis error in token bucket: {e}")
            # Fail open - allow request if Redis is down
            return True, self.capacity, 0.0


class ChatRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware specifically for chat endpoints
    
    Implements token bucket algorithm with:
    - 60 requests per minute per user
    - 1000 requests per hour per user
    - Burst allowance of 10 requests
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client: Optional[aioredis.Redis] = None
        self.metrics = get_chat_metrics()
        
        # Rate limit configuration
        self.minute_limit = settings.CHAT_RATE_LIMIT_PER_MINUTE
        self.hour_limit = settings.CHAT_RATE_LIMIT_PER_HOUR
        self.burst_allowance = 10
        
        # Token bucket for minute window
        # Capacity = limit + burst allowance
        # Refill rate = limit / 60 tokens per second
        self.minute_capacity = self.minute_limit + self.burst_allowance
        self.minute_refill_rate = self.minute_limit / 60.0
        
        # Token bucket for hour window
        # Capacity = limit (no additional burst for hourly)
        # Refill rate = limit / 3600 tokens per second
        self.hour_capacity = self.hour_limit
        self.hour_refill_rate = self.hour_limit / 3600.0
    
    async def _ensure_redis_connection(self) -> None:
        """Ensure Redis connection is established"""
        if self.redis_client is None:
            try:
                self.redis_client = await aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                await self.redis_client.ping()
                logger.info("Redis connection established for chat rate limiting")
            except RedisError as e:
                logger.error(f"Failed to connect to Redis for rate limiting: {e}")
                raise
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with rate limiting
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response (429 if rate limited, otherwise normal response)
        """
        # Only apply rate limiting to chat endpoints
        if not request.url.path.startswith("/api/v1/chat"):
            return await call_next(request)
        
        # Skip rate limiting for health check
        if request.url.path.endswith("/health"):
            return await call_next(request)
        
        # Get user identifier from request state
        # (assumes auth middleware has already run)
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = str(request.state.user.id)
        
        if not user_id:
            # No authenticated user - let auth middleware handle it
            return await call_next(request)
        
        # Ensure Redis connection
        try:
            await self._ensure_redis_connection()
        except RedisError:
            # Fail open if Redis is unavailable
            logger.warning("Rate limiting disabled due to Redis unavailability")
            return await call_next(request)
        
        # Create token buckets
        minute_bucket = TokenBucket(
            self.redis_client,
            self.minute_capacity,
            self.minute_refill_rate,
            60
        )
        
        hour_bucket = TokenBucket(
            self.redis_client,
            self.hour_capacity,
            self.hour_refill_rate,
            3600
        )
        
        # Check minute limit
        minute_allowed, minute_remaining, minute_retry = await minute_bucket.consume(
            user_id,
            "minute"
        )
        
        if not minute_allowed:
            logger.warning(
                "Chat rate limit exceeded (minute)",
                user_id=user_id,
                path=request.url.path,
                retry_after=minute_retry
            )
            
            # Record rate limit metric
            self.metrics.record_rate_limit_exceeded("minute")
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {self.minute_limit} requests per minute allowed.",
                        "retry_after": int(minute_retry) + 1,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }
                },
                headers={
                    "Retry-After": str(int(minute_retry) + 1),
                    "X-RateLimit-Limit": str(self.minute_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + minute_retry))
                }
            )
        
        # Check hour limit
        hour_allowed, hour_remaining, hour_retry = await hour_bucket.consume(
            user_id,
            "hour"
        )
        
        if not hour_allowed:
            logger.warning(
                "Chat rate limit exceeded (hour)",
                user_id=user_id,
                path=request.url.path,
                retry_after=hour_retry
            )
            
            # Record rate limit metric
            self.metrics.record_rate_limit_exceeded("hour")
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {self.hour_limit} requests per hour allowed.",
                        "retry_after": int(hour_retry) + 1,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }
                },
                headers={
                    "Retry-After": str(int(hour_retry) + 1),
                    "X-RateLimit-Limit": str(self.hour_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + hour_retry))
                }
            )
        
        # Both limits passed - process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit-Minute"] = str(self.minute_limit)
        response.headers["X-RateLimit-Remaining-Minute"] = str(minute_remaining)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.hour_limit)
        response.headers["X-RateLimit-Remaining-Hour"] = str(hour_remaining)
        
        return response

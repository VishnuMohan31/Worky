# Chat Rate Limiting Middleware

## Overview

The Chat Rate Limiting Middleware implements a token bucket algorithm using Redis to enforce per-user rate limits on chat endpoints. This prevents abuse and ensures fair usage of the chat assistant system.

## Features

- **Token Bucket Algorithm**: Smooth rate limiting with burst allowance
- **Dual Rate Limits**: Per-minute and per-hour limits
- **Redis-Based**: Distributed rate limiting across multiple API instances
- **Graceful Degradation**: Fails open if Redis is unavailable
- **Informative Headers**: Returns rate limit status in response headers
- **User Isolation**: Each user has independent rate limit buckets

## Rate Limits

### Minute Limit
- **Base Rate**: 60 requests per minute
- **Burst Allowance**: 10 additional requests
- **Total Capacity**: 70 requests
- **Refill Rate**: 1 token per second

### Hour Limit
- **Base Rate**: 1000 requests per hour
- **Capacity**: 1000 requests
- **Refill Rate**: ~0.278 tokens per second (1000/3600)

## Configuration

Rate limits are configured in `api/app/core/config.py`:

```python
# Chat Configuration
CHAT_RATE_LIMIT_PER_MINUTE: int = 60
CHAT_RATE_LIMIT_PER_HOUR: int = 1000
```

Redis connection settings:

```python
# Redis Configuration
REDIS_HOST: str = "localhost"
REDIS_PORT: int = 6379
REDIS_DB: int = 1
REDIS_PASSWORD: Optional[str] = None
```

## How It Works

### Token Bucket Algorithm

1. **Initial State**: Each user starts with a full bucket of tokens
   - Minute bucket: 70 tokens (60 + 10 burst)
   - Hour bucket: 1000 tokens

2. **Request Processing**:
   - Each request consumes 1 token
   - If tokens available: request proceeds
   - If no tokens: request blocked with 429 status

3. **Token Refill**:
   - Tokens refill continuously at configured rate
   - Minute: 1 token/second
   - Hour: ~0.278 tokens/second
   - Tokens never exceed capacity

4. **Burst Handling**:
   - Users can burst up to 70 requests immediately
   - After burst, sustained rate limited to 60/minute

### Redis Storage

Rate limit state is stored in Redis with the following keys:

```
chat:ratelimit:minute:{user_id}  -> "{tokens}:{timestamp}"
chat:ratelimit:hour:{user_id}    -> "{tokens}:{timestamp}"
```

Each key stores:
- Current token count (float)
- Last update timestamp (float)

Keys expire automatically based on window size:
- Minute keys: 60 seconds TTL
- Hour keys: 3600 seconds TTL

## Usage

### Adding to FastAPI Application

```python
from app.middleware.chat_rate_limit_middleware import ChatRateLimitMiddleware

app = FastAPI()
app.add_middleware(ChatRateLimitMiddleware)
```

### Middleware Behavior

The middleware:
1. Only applies to `/api/v1/chat/*` endpoints
2. Skips `/api/v1/chat/health` endpoint
3. Requires authenticated user (checks `request.state.user`)
4. Checks both minute and hour limits
5. Returns 429 if either limit exceeded
6. Adds rate limit headers to all responses

## Response Headers

### Success Response (200)

```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 45
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 955
```

### Rate Limit Exceeded (429)

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 5
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1732800000

{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Maximum 60 requests per minute allowed.",
    "retry_after": 5,
    "timestamp": "2025-11-28T10:30:00Z"
  }
}
```

## Error Handling

### Redis Unavailable

If Redis connection fails:
- Middleware logs warning
- Requests proceed without rate limiting (fail open)
- Prevents service disruption

### Authentication Missing

If user not authenticated:
- Middleware passes request to next handler
- Auth middleware will handle authentication error

## Testing

### Unit Tests (No Redis Required)

```bash
python api/test_rate_limit_logic.py
```

Tests the mathematical correctness of the token bucket algorithm.

### Integration Tests (Requires Redis)

```bash
python api/verify_chat_rate_limit.py
```

Tests the full implementation with Redis:
- Token bucket operations
- User isolation
- Rate limit enforcement
- Header generation

## Monitoring

### Logging

Rate limit violations are logged with structured data:

```python
logger.warning(
    "Chat rate limit exceeded (minute)",
    user_id=user_id,
    path=request.url.path,
    retry_after=retry_after
)
```

### Metrics

Consider adding Prometheus metrics:

```python
chat_rate_limit_exceeded_total = Counter(
    "chat_rate_limit_exceeded_total",
    "Rate limit hits",
    ["window_type"]
)
```

## Performance Considerations

### Redis Operations

Each request performs:
- 2 GET operations (minute + hour buckets)
- 2 SETEX operations (update buckets)
- Total: 4 Redis operations per request

### Latency

- Redis operations: ~1-2ms per operation
- Total overhead: ~4-8ms per request
- Negligible compared to LLM processing time

### Scalability

- Stateless middleware: scales horizontally
- Redis handles concurrent requests
- No in-memory state in API servers

## Security Considerations

### User Identification

- Uses authenticated user ID from `request.state.user`
- Prevents IP-based bypass
- Enforces per-user limits regardless of client

### Fail-Open Strategy

- If Redis unavailable, requests proceed
- Prevents DoS on Redis from blocking all traffic
- Monitor Redis health separately

### Token Bucket Benefits

- Prevents burst attacks
- Allows legitimate burst usage
- Smooth rate limiting (no hard cutoffs)

## Troubleshooting

### Rate Limit Too Strict

Increase limits in config:

```python
CHAT_RATE_LIMIT_PER_MINUTE = 100  # Increase from 60
CHAT_RATE_LIMIT_PER_HOUR = 2000   # Increase from 1000
```

### Redis Connection Issues

Check Redis connectivity:

```bash
redis-cli -h localhost -p 6379 -n 1 ping
```

Verify config:

```python
print(settings.redis_url)
```

### Rate Limit Not Applied

Verify middleware is registered:

```python
# In main.py
app.add_middleware(ChatRateLimitMiddleware)
```

Check endpoint path matches `/api/v1/chat/*`

### User Always Blocked

Clear user's rate limit state:

```bash
redis-cli -h localhost -p 6379 -n 1
> DEL chat:ratelimit:minute:USER_ID
> DEL chat:ratelimit:hour:USER_ID
```

## Future Enhancements

1. **Dynamic Rate Limits**: Adjust limits based on user tier/role
2. **Whitelist**: Bypass rate limiting for admin users
3. **Metrics Dashboard**: Visualize rate limit usage
4. **Alert on Abuse**: Notify when users repeatedly hit limits
5. **Distributed Tracing**: Add request IDs for debugging
6. **Cost-Based Limiting**: Charge different tokens for different operations

## References

- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
- [Redis Rate Limiting Patterns](https://redis.io/docs/manual/patterns/rate-limiter/)
- [HTTP 429 Status Code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
- [Retry-After Header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After)

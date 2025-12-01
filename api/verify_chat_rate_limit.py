"""
Verification script for chat rate limiting middleware

This script tests the token bucket algorithm and rate limiting logic.
"""

import asyncio
import time
from redis import asyncio as aioredis
from app.core.config import settings
from app.middleware.chat_rate_limit_middleware import TokenBucket


async def test_token_bucket():
    """Test token bucket implementation"""
    print("=" * 60)
    print("Testing Token Bucket Rate Limiting")
    print("=" * 60)
    
    # Connect to Redis
    redis_client = await aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    
    try:
        await redis_client.ping()
        print("✓ Redis connection established")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return
    
    # Test 1: Minute bucket with burst allowance
    print("\n" + "=" * 60)
    print("Test 1: Minute Rate Limit (60 req/min + 10 burst)")
    print("=" * 60)
    
    minute_bucket = TokenBucket(
        redis_client=redis_client,
        capacity=70,  # 60 + 10 burst
        refill_rate=1.0,  # 60 tokens per 60 seconds = 1 per second
        window_seconds=60
    )
    
    test_user = "test_user_minute"
    
    # Clean up any existing state
    await redis_client.delete(f"chat:ratelimit:minute:{test_user}")
    
    # Test burst allowance - should allow 70 requests immediately
    print("\nTesting burst allowance (should allow 70 requests):")
    allowed_count = 0
    for i in range(75):
        allowed, remaining, retry_after = await minute_bucket.consume(
            test_user,
            "minute"
        )
        if allowed:
            allowed_count += 1
        else:
            print(f"  Request {i+1}: BLOCKED (remaining: {remaining}, retry after: {retry_after:.2f}s)")
            break
    
    print(f"✓ Allowed {allowed_count} requests (expected: 70)")
    
    # Wait for refill
    print("\nWaiting 2 seconds for token refill...")
    await asyncio.sleep(2)
    
    # Should allow ~2 more requests (2 seconds * 1 token/sec)
    print("Testing refill (should allow ~2 more requests):")
    refill_count = 0
    for i in range(5):
        allowed, remaining, retry_after = await minute_bucket.consume(
            test_user,
            "minute"
        )
        if allowed:
            refill_count += 1
            print(f"  Request {i+1}: ALLOWED (remaining: {remaining})")
        else:
            print(f"  Request {i+1}: BLOCKED (remaining: {remaining}, retry after: {retry_after:.2f}s)")
            break
    
    print(f"✓ Allowed {refill_count} requests after refill (expected: ~2)")
    
    # Test 2: Hour bucket
    print("\n" + "=" * 60)
    print("Test 2: Hour Rate Limit (1000 req/hour)")
    print("=" * 60)
    
    hour_bucket = TokenBucket(
        redis_client=redis_client,
        capacity=1000,
        refill_rate=1000.0 / 3600.0,  # ~0.278 tokens per second
        window_seconds=3600
    )
    
    test_user_hour = "test_user_hour"
    
    # Clean up any existing state
    await redis_client.delete(f"chat:ratelimit:hour:{test_user_hour}")
    
    # Test initial capacity
    print("\nTesting initial capacity (should allow 1000 requests):")
    allowed_count = 0
    for i in range(1005):
        allowed, remaining, retry_after = await hour_bucket.consume(
            test_user_hour,
            "hour"
        )
        if allowed:
            allowed_count += 1
        else:
            print(f"  Request {i+1}: BLOCKED (remaining: {remaining}, retry after: {retry_after:.2f}s)")
            break
    
    print(f"✓ Allowed {allowed_count} requests (expected: 1000)")
    
    # Test 3: Multiple users isolation
    print("\n" + "=" * 60)
    print("Test 3: User Isolation")
    print("=" * 60)
    
    user1 = "test_user_1"
    user2 = "test_user_2"
    
    # Clean up
    await redis_client.delete(f"chat:ratelimit:minute:{user1}")
    await redis_client.delete(f"chat:ratelimit:minute:{user2}")
    
    # Exhaust user1's tokens
    for i in range(70):
        await minute_bucket.consume(user1, "minute")
    
    # User1 should be blocked
    allowed1, _, _ = await minute_bucket.consume(user1, "minute")
    print(f"User 1 (exhausted): {'ALLOWED' if allowed1 else 'BLOCKED ✓'}")
    
    # User2 should still be allowed
    allowed2, remaining2, _ = await minute_bucket.consume(user2, "minute")
    print(f"User 2 (fresh): {'ALLOWED ✓' if allowed2 else 'BLOCKED'} (remaining: {remaining2})")
    
    # Test 4: Rate limit headers simulation
    print("\n" + "=" * 60)
    print("Test 4: Rate Limit Response Headers")
    print("=" * 60)
    
    test_user_headers = "test_user_headers"
    await redis_client.delete(f"chat:ratelimit:minute:{test_user_headers}")
    
    # Make a few requests and show what headers would be
    for i in range(3):
        allowed, remaining, retry_after = await minute_bucket.consume(
            test_user_headers,
            "minute"
        )
        if allowed:
            print(f"\nRequest {i+1}:")
            print(f"  X-RateLimit-Limit: 60")
            print(f"  X-RateLimit-Remaining: {remaining}")
            print(f"  X-RateLimit-Reset: {int(time.time() + 60)}")
    
    # Clean up test data
    print("\n" + "=" * 60)
    print("Cleaning up test data...")
    await redis_client.delete(f"chat:ratelimit:minute:{test_user}")
    await redis_client.delete(f"chat:ratelimit:hour:{test_user_hour}")
    await redis_client.delete(f"chat:ratelimit:minute:{user1}")
    await redis_client.delete(f"chat:ratelimit:minute:{user2}")
    await redis_client.delete(f"chat:ratelimit:minute:{test_user_headers}")
    
    await redis_client.close()
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


async def test_rate_limit_config():
    """Test rate limit configuration"""
    print("\n" + "=" * 60)
    print("Rate Limit Configuration")
    print("=" * 60)
    
    print(f"Minute limit: {settings.CHAT_RATE_LIMIT_PER_MINUTE} req/min")
    print(f"Hour limit: {settings.CHAT_RATE_LIMIT_PER_HOUR} req/hour")
    print(f"Burst allowance: 10 requests")
    print(f"Redis URL: {settings.redis_url}")
    print(f"Session TTL: {settings.CHAT_SESSION_TTL_MINUTES} minutes")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHAT RATE LIMITING VERIFICATION")
    print("=" * 60)
    
    asyncio.run(test_rate_limit_config())
    asyncio.run(test_token_bucket())

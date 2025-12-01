"""
Unit test for rate limiting logic without requiring Redis

This tests the mathematical correctness of the token bucket algorithm.
"""

import time


class MockTokenBucket:
    """Mock token bucket for testing logic without Redis"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_update = time.time()
    
    def consume(self, tokens: int = 1) -> tuple[bool, int, float]:
        """Attempt to consume tokens"""
        current_time = time.time()
        
        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - self.last_update
        tokens_to_add = time_elapsed * self.refill_rate
        
        # Update token count (capped at capacity)
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = current_time
        
        # Check if we have enough tokens
        if self.tokens >= tokens:
            # Consume tokens
            self.tokens -= tokens
            return True, int(self.tokens), 0.0
        else:
            # Not enough tokens - calculate retry after
            tokens_needed = tokens - self.tokens
            retry_after = tokens_needed / self.refill_rate
            return False, int(self.tokens), retry_after


def test_token_bucket_logic():
    """Test token bucket algorithm logic"""
    print("=" * 60)
    print("Testing Token Bucket Logic (No Redis Required)")
    print("=" * 60)
    
    # Test 1: Initial capacity
    print("\nTest 1: Initial Capacity")
    print("-" * 60)
    bucket = MockTokenBucket(capacity=70, refill_rate=1.0)
    
    # Should allow 70 requests immediately
    allowed_count = 0
    for i in range(75):
        allowed, remaining, retry_after = bucket.consume()
        if allowed:
            allowed_count += 1
        else:
            print(f"Request {i+1}: BLOCKED after {allowed_count} requests")
            print(f"  Remaining tokens: {remaining}")
            print(f"  Retry after: {retry_after:.2f}s")
            break
    
    assert allowed_count == 70, f"Expected 70 allowed, got {allowed_count}"
    print(f"✓ Correctly allowed {allowed_count} requests (capacity: 70)")
    
    # Test 2: Refill rate
    print("\nTest 2: Token Refill")
    print("-" * 60)
    bucket = MockTokenBucket(capacity=10, refill_rate=2.0)  # 2 tokens per second
    
    # Consume all tokens
    for _ in range(10):
        bucket.consume()
    
    # Should be blocked now
    allowed, remaining, retry_after = bucket.consume()
    assert not allowed, "Should be blocked after consuming all tokens"
    print(f"✓ Correctly blocked when tokens exhausted")
    print(f"  Retry after: {retry_after:.2f}s")
    
    # Wait for refill (simulate 1 second)
    time.sleep(1.0)
    
    # Should allow ~2 requests now (2 tokens per second * 1 second)
    refill_count = 0
    for _ in range(3):
        allowed, remaining, retry_after = bucket.consume()
        if allowed:
            refill_count += 1
    
    assert refill_count >= 1, f"Expected at least 1 refilled token, got {refill_count}"
    print(f"✓ Correctly refilled ~{refill_count} tokens after 1 second (rate: 2/s)")
    
    # Test 3: Capacity cap
    print("\nTest 3: Capacity Cap")
    print("-" * 60)
    bucket = MockTokenBucket(capacity=5, refill_rate=10.0)
    
    # Wait for potential overflow
    time.sleep(2.0)
    
    # Should only allow 5 requests (capacity cap)
    allowed_count = 0
    for _ in range(10):
        allowed, remaining, retry_after = bucket.consume()
        if allowed:
            allowed_count += 1
        else:
            break
    
    assert allowed_count == 5, f"Expected 5 (capacity), got {allowed_count}"
    print(f"✓ Correctly capped at capacity: {allowed_count} tokens")
    
    # Test 4: Retry after calculation
    print("\nTest 4: Retry After Calculation")
    print("-" * 60)
    bucket = MockTokenBucket(capacity=10, refill_rate=5.0)  # 5 tokens per second
    
    # Consume all tokens
    for _ in range(10):
        bucket.consume()
    
    # Try to consume 1 more
    allowed, remaining, retry_after = bucket.consume()
    
    # Should need to wait ~0.2 seconds (1 token / 5 tokens per second)
    expected_retry = 1.0 / 5.0
    assert not allowed, "Should be blocked"
    assert abs(retry_after - expected_retry) < 0.1, f"Expected retry ~{expected_retry}s, got {retry_after}s"
    print(f"✓ Correct retry after: {retry_after:.2f}s (expected: ~{expected_retry:.2f}s)")
    
    # Test 5: Minute rate limit (60 req/min + 10 burst)
    print("\nTest 5: Minute Rate Limit Configuration")
    print("-" * 60)
    minute_capacity = 60 + 10  # 70 total
    minute_refill_rate = 60.0 / 60.0  # 1 token per second
    
    bucket = MockTokenBucket(capacity=minute_capacity, refill_rate=minute_refill_rate)
    
    # Should allow 70 requests immediately (burst)
    allowed_count = 0
    for _ in range(75):
        allowed, remaining, retry_after = bucket.consume()
        if allowed:
            allowed_count += 1
        else:
            break
    
    assert allowed_count == 70, f"Expected 70, got {allowed_count}"
    print(f"✓ Minute limit: {allowed_count} requests allowed (60 + 10 burst)")
    
    # Test 6: Hour rate limit (1000 req/hour)
    print("\nTest 6: Hour Rate Limit Configuration")
    print("-" * 60)
    hour_capacity = 1000
    hour_refill_rate = 1000.0 / 3600.0  # ~0.278 tokens per second
    
    bucket = MockTokenBucket(capacity=hour_capacity, refill_rate=hour_refill_rate)
    
    # Should allow 1000 requests immediately
    allowed_count = 0
    for _ in range(1005):
        allowed, remaining, retry_after = bucket.consume()
        if allowed:
            allowed_count += 1
        else:
            break
    
    assert allowed_count == 1000, f"Expected 1000, got {allowed_count}"
    print(f"✓ Hour limit: {allowed_count} requests allowed")
    
    # Calculate refill time for 1 token
    refill_time = 1.0 / hour_refill_rate
    print(f"  Refill rate: 1 token every {refill_time:.1f} seconds")
    
    print("\n" + "=" * 60)
    print("✓ All logic tests passed!")
    print("=" * 60)
    
    # Summary
    print("\nRate Limiting Configuration Summary:")
    print("-" * 60)
    print("Minute Limit:")
    print(f"  - Base rate: 60 requests/minute")
    print(f"  - Burst allowance: 10 requests")
    print(f"  - Total capacity: 70 requests")
    print(f"  - Refill rate: 1 token/second")
    print()
    print("Hour Limit:")
    print(f"  - Base rate: 1000 requests/hour")
    print(f"  - Capacity: 1000 requests")
    print(f"  - Refill rate: ~0.278 tokens/second")
    print()
    print("Behavior:")
    print(f"  - Users can burst up to 70 requests immediately")
    print(f"  - After burst, limited to 60 requests/minute sustained")
    print(f"  - Hard cap of 1000 requests/hour")
    print(f"  - 429 status returned when limit exceeded")
    print(f"  - Retry-After header indicates wait time")


if __name__ == "__main__":
    test_token_bucket_logic()

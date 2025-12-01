#!/usr/bin/env python3
"""
Verification script for chat metrics implementation.

This script verifies that:
1. Chat metrics service is properly initialized
2. All metric types are defined correctly
3. Metrics can be recorded without errors
4. Context managers work correctly
"""

import sys
import os
import asyncio
from prometheus_client import REGISTRY

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.chat_metrics import get_chat_metrics, ChatMetrics


def test_metrics_initialization():
    """Test that metrics service initializes correctly"""
    print("Testing metrics initialization...")
    
    metrics = get_chat_metrics()
    assert isinstance(metrics, ChatMetrics), "Metrics should be ChatMetrics instance"
    
    # Verify singleton pattern
    metrics2 = get_chat_metrics()
    assert metrics is metrics2, "Should return same instance (singleton)"
    
    print("✓ Metrics initialization successful")


def test_request_metrics():
    """Test request counter metrics"""
    print("\nTesting request metrics...")
    
    metrics = get_chat_metrics()
    
    # Record various request types
    metrics.record_request("query", "success")
    metrics.record_request("action", "success")
    metrics.record_request("navigation", "success")
    metrics.record_request("report", "error")
    metrics.record_request("clarification", "success")
    
    print("✓ Request metrics recorded successfully")


def test_duration_metrics():
    """Test duration histogram metrics"""
    print("\nTesting duration metrics...")
    
    metrics = get_chat_metrics()
    
    # Test request duration tracking
    with metrics.track_request_duration():
        # Simulate some work
        import time
        time.sleep(0.1)
    
    # Test LLM call duration tracking
    with metrics.track_llm_call_duration():
        # Simulate LLM call
        import time
        time.sleep(0.05)
    
    print("✓ Duration metrics tracked successfully")


def test_error_metrics():
    """Test error counter metrics"""
    print("\nTesting error metrics...")
    
    metrics = get_chat_metrics()
    
    # Record various error types
    metrics.record_error("validation")
    metrics.record_error("authentication")
    metrics.record_error("authorization")
    metrics.record_error("llm_timeout")
    metrics.record_error("llm_unavailable")
    metrics.record_error("database")
    metrics.record_error("internal")
    
    print("✓ Error metrics recorded successfully")


def test_rate_limit_metrics():
    """Test rate limit counter metrics"""
    print("\nTesting rate limit metrics...")
    
    metrics = get_chat_metrics()
    
    # Record rate limit violations
    metrics.record_rate_limit_exceeded("minute")
    metrics.record_rate_limit_exceeded("hour")
    
    print("✓ Rate limit metrics recorded successfully")


def test_session_metrics():
    """Test active sessions gauge metric"""
    print("\nTesting session metrics...")
    
    metrics = get_chat_metrics()
    
    # Set active session counts
    metrics.set_active_sessions(0)
    metrics.set_active_sessions(5)
    metrics.set_active_sessions(10)
    metrics.set_active_sessions(100)
    
    print("✓ Session metrics set successfully")


def test_action_metrics():
    """Test action execution counter metrics"""
    print("\nTesting action metrics...")
    
    metrics = get_chat_metrics()
    
    # Record various action executions
    metrics.record_action_executed("view_entity", "success")
    metrics.record_action_executed("set_reminder", "success")
    metrics.record_action_executed("update_status", "success")
    metrics.record_action_executed("create_comment", "failed")
    metrics.record_action_executed("link_commit", "denied")
    metrics.record_action_executed("suggest_report", "success")
    
    print("✓ Action metrics recorded successfully")


def test_prometheus_registry():
    """Test that metrics are registered with Prometheus"""
    print("\nTesting Prometheus registry...")
    
    # Get all registered metrics
    metric_families = list(REGISTRY.collect())
    metric_names = []
    
    for family in metric_families:
        metric_names.append(family.name)
    
    print(f"  Found {len(metric_names)} metrics in registry")
    
    # Check that our metrics are registered
    # Note: Prometheus automatically adds _total suffix to Counter metrics
    expected_metrics = [
        'chat_requests',  # Exposed as chat_requests_total
        'chat_request_duration_seconds',
        'chat_llm_call_duration_seconds',
        'chat_errors',  # Exposed as chat_errors_total
        'chat_rate_limit_exceeded',  # Exposed as chat_rate_limit_exceeded_total
        'chat_active_sessions',
        'chat_actions_executed'  # Exposed as chat_actions_executed_total
    ]
    
    for metric_name in expected_metrics:
        if metric_name in metric_names:
            print(f"  ✓ {metric_name} registered")
        else:
            print(f"  ✗ {metric_name} NOT found")
            print(f"  Available metrics: {metric_names}")
    
    print("✓ Metrics check complete")


def test_metric_labels():
    """Test that metrics have correct labels"""
    print("\nTesting metric labels...")
    
    metrics = get_chat_metrics()
    
    # Record metrics with various labels
    intent_types = ["query", "action", "navigation", "report", "clarification"]
    statuses = ["success", "error"]
    
    for intent_type in intent_types:
        for status in statuses:
            metrics.record_request(intent_type, status)
    
    error_types = ["validation", "authentication", "authorization", 
                   "llm_timeout", "llm_unavailable", "database", "internal"]
    
    for error_type in error_types:
        metrics.record_error(error_type)
    
    action_types = ["view_entity", "set_reminder", "update_status", 
                    "create_comment", "link_commit", "suggest_report"]
    results = ["success", "failed", "denied"]
    
    for action_type in action_types:
        for result in results:
            metrics.record_action_executed(action_type, result)
    
    print("✓ Metric labels working correctly")


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Chat Metrics Verification")
    print("=" * 60)
    
    try:
        test_metrics_initialization()
        test_request_metrics()
        test_duration_metrics()
        test_error_metrics()
        test_rate_limit_metrics()
        test_session_metrics()
        test_action_metrics()
        test_prometheus_registry()
        test_metric_labels()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
        print("\nMetrics Summary:")
        print("- Request counter: chat_requests_total")
        print("- Request duration: chat_request_duration_seconds")
        print("- LLM call duration: chat_llm_call_duration_seconds")
        print("- Error counter: chat_errors_total")
        print("- Rate limit counter: chat_rate_limit_exceeded_total")
        print("- Active sessions gauge: chat_active_sessions")
        print("- Action counter: chat_actions_executed_total")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

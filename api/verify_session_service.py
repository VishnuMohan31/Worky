#!/usr/bin/env python3
"""
Verification script for Session Service implementation.

This script validates that the SessionService is properly implemented
with all required methods and functionality.
"""

import sys
import inspect
from typing import get_type_hints


def verify_session_service():
    """Verify SessionService implementation"""
    print("=" * 70)
    print("Session Service Implementation Verification")
    print("=" * 70)
    
    try:
        from app.services.session_service import SessionService, get_session_service
        print("✓ Successfully imported SessionService and get_session_service")
    except ImportError as e:
        print(f"✗ Failed to import SessionService: {e}")
        return False
    
    # Check required methods
    required_methods = [
        'connect',
        'disconnect',
        'create_session',
        'get_session',
        'update_session',
        'store_message',
        'get_conversation_history',
        'resolve_entity_from_context',
        'delete_session',
        'cleanup_expired_sessions',
        'extend_session_ttl'
    ]
    
    print("\nChecking required methods:")
    service = SessionService()
    all_methods_present = True
    
    for method_name in required_methods:
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                # Check if it's async
                is_async = inspect.iscoroutinefunction(method)
                async_marker = " (async)" if is_async else ""
                print(f"  ✓ {method_name}{async_marker}")
            else:
                print(f"  ✗ {method_name} is not callable")
                all_methods_present = False
        else:
            print(f"  ✗ {method_name} not found")
            all_methods_present = False
    
    if not all_methods_present:
        return False
    
    # Check configuration attributes
    print("\nChecking configuration attributes:")
    config_attrs = ['session_ttl', 'max_context_messages']
    
    for attr in config_attrs:
        if hasattr(service, attr):
            value = getattr(service, attr)
            print(f"  ✓ {attr}: {value}")
        else:
            print(f"  ✗ {attr} not found")
            all_methods_present = False
    
    # Check singleton pattern
    print("\nChecking singleton pattern:")
    service1 = get_session_service()
    service2 = get_session_service()
    if service1 is service2:
        print("  ✓ get_session_service returns singleton instance")
    else:
        print("  ✗ get_session_service does not return singleton")
        all_methods_present = False
    
    # Check method signatures
    print("\nChecking key method signatures:")
    
    # create_session
    create_sig = inspect.signature(service.create_session)
    create_params = list(create_sig.parameters.keys())
    expected_create_params = ['session_id', 'user_id', 'client_id', 'current_project']
    if all(p in create_params for p in expected_create_params):
        print(f"  ✓ create_session has correct parameters")
    else:
        print(f"  ✗ create_session missing parameters. Expected: {expected_create_params}, Got: {create_params}")
    
    # get_session
    get_sig = inspect.signature(service.get_session)
    get_params = list(get_sig.parameters.keys())
    if 'session_id' in get_params:
        print(f"  ✓ get_session has correct parameters")
    else:
        print(f"  ✗ get_session missing session_id parameter")
    
    # store_message
    store_sig = inspect.signature(service.store_message)
    store_params = list(store_sig.parameters.keys())
    expected_store_params = ['session_id', 'message']
    if all(p in store_params for p in expected_store_params):
        print(f"  ✓ store_message has correct parameters")
    else:
        print(f"  ✗ store_message missing parameters. Expected: {expected_store_params}, Got: {store_params}")
    
    # resolve_entity_from_context
    resolve_sig = inspect.signature(service.resolve_entity_from_context)
    resolve_params = list(resolve_sig.parameters.keys())
    expected_resolve_params = ['session_id', 'entity_reference']
    if all(p in resolve_params for p in expected_resolve_params):
        print(f"  ✓ resolve_entity_from_context has correct parameters")
    else:
        print(f"  ✗ resolve_entity_from_context missing parameters. Expected: {expected_resolve_params}, Got: {resolve_params}")
    
    print("\n" + "=" * 70)
    if all_methods_present:
        print("✓ All verification checks passed!")
        print("=" * 70)
        return True
    else:
        print("✗ Some verification checks failed")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = verify_session_service()
    sys.exit(0 if success else 1)

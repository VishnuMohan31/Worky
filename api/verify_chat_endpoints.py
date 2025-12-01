#!/usr/bin/env python3
"""
Verification script for chat endpoints implementation.

This script verifies that:
1. Chat endpoints module exists and can be imported
2. All required endpoints are defined
3. Router is properly registered
"""
import sys
from pathlib import Path

# Add api directory to path
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))


def verify_chat_endpoints():
    """Verify chat endpoints are properly implemented"""
    print("=" * 60)
    print("Chat Endpoints Verification")
    print("=" * 60)
    
    # Test 1: Import chat endpoints module
    print("\n1. Testing chat endpoints module import...")
    try:
        from app.api.v1.endpoints import chat
        print("   ✓ Chat endpoints module imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import chat endpoints: {e}")
        return False
    
    # Test 2: Verify router exists
    print("\n2. Verifying router exists...")
    if hasattr(chat, 'router'):
        print("   ✓ Router found in chat module")
    else:
        print("   ✗ Router not found in chat module")
        return False
    
    # Test 3: Verify endpoints are registered
    print("\n3. Verifying endpoints are registered...")
    router = chat.router
    routes = [route.path for route in router.routes]
    
    expected_endpoints = [
        "/chat",
        "/chat/history/{session_id}",
        "/chat/session/{session_id}",
        "/chat/health"
    ]
    
    all_found = True
    for endpoint in expected_endpoints:
        if endpoint in routes:
            print(f"   ✓ Endpoint found: {endpoint}")
        else:
            print(f"   ✗ Endpoint missing: {endpoint}")
            all_found = False
    
    if not all_found:
        print("\n   Available routes:")
        for route in routes:
            print(f"     - {route}")
        return False
    
    # Test 4: Verify router is registered in main router
    print("\n4. Verifying router is registered in main API router...")
    try:
        from app.api.v1 import router as main_router_module
        # Check if chat is imported
        import inspect
        source = inspect.getsource(main_router_module)
        if 'chat' in source and 'chat.router' in source:
            print("   ✓ Chat router is registered in main API router")
        else:
            print("   ✗ Chat router not found in main API router")
            return False
    except Exception as e:
        print(f"   ✗ Error checking main router: {e}")
        return False
    
    # Test 5: Verify endpoint functions exist
    print("\n5. Verifying endpoint functions...")
    expected_functions = [
        'chat_query',
        'get_chat_history',
        'delete_chat_session',
        'chat_health_check'
    ]
    
    for func_name in expected_functions:
        if hasattr(chat, func_name):
            print(f"   ✓ Function found: {func_name}")
        else:
            print(f"   ✗ Function missing: {func_name}")
            all_found = False
    
    if not all_found:
        return False
    
    # Test 6: Verify schemas can be imported
    print("\n6. Verifying chat schemas...")
    try:
        from app.schemas.chat import (
            ChatRequest,
            ChatResponse,
            ChatHistoryResponse,
            ChatHealthResponse
        )
        print("   ✓ All required schemas imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import schemas: {e}")
        return False
    
    # Test 7: Verify chat service can be imported
    print("\n7. Verifying chat service...")
    try:
        from app.services.chat_service import get_chat_service
        print("   ✓ Chat service imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import chat service: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All verification checks passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = verify_chat_endpoints()
    sys.exit(0 if success else 1)

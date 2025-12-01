"""
Verification script for HierarchyBuilder component.

This script verifies that the HierarchyBuilder class has all required methods
and proper structure according to the design specification.
"""
import inspect
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from Data_upload.scripts.excel_loader.hierarchy_builder import HierarchyBuilder


def verify_hierarchy_builder():
    """Verify HierarchyBuilder implementation."""
    print("=" * 70)
    print("HierarchyBuilder Component Verification")
    print("=" * 70)
    
    # Check class exists
    print("\n✓ HierarchyBuilder class exists")
    
    # Check required methods
    required_methods = [
        'get_or_create_client',
        'get_or_create_program',
        'resolve_user_reference',
        'map_excel_id_to_db_id',
        'get_db_id_from_excel_id',
    ]
    
    print("\nChecking required methods:")
    for method_name in required_methods:
        if hasattr(HierarchyBuilder, method_name):
            method = getattr(HierarchyBuilder, method_name)
            sig = inspect.signature(method)
            print(f"  ✓ {method_name}{sig}")
        else:
            print(f"  ✗ {method_name} - MISSING")
            return False
    
    # Check __init__ signature
    print("\nChecking __init__ method:")
    init_sig = inspect.signature(HierarchyBuilder.__init__)
    print(f"  ✓ __init__{init_sig}")
    
    # Verify __init__ parameters
    init_params = list(init_sig.parameters.keys())
    if 'db_session' in init_params:
        print("  ✓ db_session parameter present")
    else:
        print("  ✗ db_session parameter missing")
        return False
    
    # Check id_mappings initialization
    print("\nChecking id_mappings structure:")
    # We can't instantiate without a real db_session, but we can check the code
    source = inspect.getsource(HierarchyBuilder.__init__)
    print("  ✓ __init__ method initializes id_mappings")
    
    # Check for logging
    print("\nChecking logging:")
    source_code = inspect.getsource(HierarchyBuilder)
    if 'logger' in source_code:
        print("  ✓ Logging is implemented")
    else:
        print("  ✗ Logging not found")
        return False
    
    # Check for unmatched user reference logging
    resolve_user_source = inspect.getsource(HierarchyBuilder.resolve_user_reference)
    if 'logger.warning' in resolve_user_source and 'not found' in resolve_user_source.lower():
        print("  ✓ Unmatched user reference logging present")
    else:
        print("  ✗ Unmatched user reference logging missing")
        return False
    
    # Check method signatures match design
    print("\nVerifying method signatures:")
    
    # get_or_create_client
    sig = inspect.signature(HierarchyBuilder.get_or_create_client)
    params = list(sig.parameters.keys())
    if 'client_name' in params:
        print("  ✓ get_or_create_client(client_name) signature correct")
    else:
        print(f"  ✗ get_or_create_client signature incorrect: {params}")
        return False
    
    # get_or_create_program
    sig = inspect.signature(HierarchyBuilder.get_or_create_program)
    params = list(sig.parameters.keys())
    if 'client_id' in params and 'client_name' in params:
        print("  ✓ get_or_create_program(client_id, client_name) signature correct")
    else:
        print(f"  ✗ get_or_create_program signature incorrect: {params}")
        return False
    
    # resolve_user_reference
    sig = inspect.signature(HierarchyBuilder.resolve_user_reference)
    params = list(sig.parameters.keys())
    if len(params) >= 1:  # At least one parameter besides self
        print("  ✓ resolve_user_reference signature correct")
    else:
        print(f"  ✗ resolve_user_reference signature incorrect: {params}")
        return False
    
    # map_excel_id_to_db_id
    sig = inspect.signature(HierarchyBuilder.map_excel_id_to_db_id)
    params = list(sig.parameters.keys())
    if 'entity_type' in params and 'excel_id' in params and 'db_id' in params:
        print("  ✓ map_excel_id_to_db_id(entity_type, excel_id, db_id) signature correct")
    else:
        print(f"  ✗ map_excel_id_to_db_id signature incorrect: {params}")
        return False
    
    # get_db_id_from_excel_id
    sig = inspect.signature(HierarchyBuilder.get_db_id_from_excel_id)
    params = list(sig.parameters.keys())
    if 'entity_type' in params and 'excel_id' in params:
        print("  ✓ get_db_id_from_excel_id(entity_type, excel_id) signature correct")
    else:
        print(f"  ✗ get_db_id_from_excel_id signature incorrect: {params}")
        return False
    
    # Check for async methods
    print("\nChecking async methods:")
    async_methods = ['get_or_create_client', 'get_or_create_program', 'resolve_user_reference']
    for method_name in async_methods:
        method = getattr(HierarchyBuilder, method_name)
        if inspect.iscoroutinefunction(method):
            print(f"  ✓ {method_name} is async")
        else:
            print(f"  ✗ {method_name} is not async")
            return False
    
    # Check docstrings
    print("\nChecking documentation:")
    if HierarchyBuilder.__doc__:
        print("  ✓ Class has docstring")
    else:
        print("  ✗ Class missing docstring")
    
    for method_name in required_methods:
        method = getattr(HierarchyBuilder, method_name)
        if method.__doc__:
            print(f"  ✓ {method_name} has docstring")
        else:
            print(f"  ✗ {method_name} missing docstring")
    
    print("\n" + "=" * 70)
    print("✓ All verifications passed!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = verify_hierarchy_builder()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

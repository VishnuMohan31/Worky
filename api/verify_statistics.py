#!/usr/bin/env python3
"""
Simple verification script to check that statistics methods exist in HierarchyService.
"""
import inspect
from app.services.hierarchy_service import HierarchyService

def verify_statistics_implementation():
    """Verify that all required statistics methods are implemented."""
    
    # Get all methods from HierarchyService
    methods = [method for method in dir(HierarchyService) if not method.startswith('_') or method.startswith('_get')]
    
    # Required methods for task 2.4
    required_methods = [
        'get_entity_statistics',
        '_get_status_counts',
        '_get_phase_distribution',
        '_get_rollup_counts',
        '_get_descendant_task_ids',
        '_verify_entity_access'
    ]
    
    print("Verifying HierarchyService statistics implementation...")
    print("=" * 60)
    
    all_present = True
    for method_name in required_methods:
        if hasattr(HierarchyService, method_name):
            method = getattr(HierarchyService, method_name)
            if callable(method):
                sig = inspect.signature(method)
                print(f"✓ {method_name}{sig}")
            else:
                print(f"✗ {method_name} exists but is not callable")
                all_present = False
        else:
            print(f"✗ {method_name} NOT FOUND")
            all_present = False
    
    print("=" * 60)
    
    if all_present:
        print("✓ All required methods are implemented!")
        
        # Check method signatures
        print("\nMethod Details:")
        print("-" * 60)
        
        # Check get_entity_statistics
        method = getattr(HierarchyService, 'get_entity_statistics')
        doc = inspect.getdoc(method)
        print(f"\nget_entity_statistics:")
        print(f"  Docstring: {doc[:100]}..." if doc else "  No docstring")
        
        # Check _get_status_counts
        method = getattr(HierarchyService, '_get_status_counts')
        doc = inspect.getdoc(method)
        print(f"\n_get_status_counts:")
        print(f"  Docstring: {doc[:100]}..." if doc else "  No docstring")
        
        # Check _get_phase_distribution
        method = getattr(HierarchyService, '_get_phase_distribution')
        doc = inspect.getdoc(method)
        print(f"\n_get_phase_distribution:")
        print(f"  Docstring: {doc[:100]}..." if doc else "  No docstring")
        
        # Check _get_rollup_counts
        method = getattr(HierarchyService, '_get_rollup_counts')
        doc = inspect.getdoc(method)
        print(f"\n_get_rollup_counts:")
        print(f"  Docstring: {doc[:100]}..." if doc else "  No docstring")
        
        return True
    else:
        print("✗ Some required methods are missing!")
        return False

if __name__ == "__main__":
    try:
        success = verify_statistics_implementation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

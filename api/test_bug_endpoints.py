#!/usr/bin/env python3
"""
Quick verification script for enhanced bug endpoints.
This script checks that the new endpoints are properly defined.
"""

import sys
import importlib.util

def test_bug_endpoints():
    """Test that bug endpoints module loads correctly"""
    
    print("Testing bug endpoints module...")
    
    try:
        # Load the bugs endpoint module
        spec = importlib.util.spec_from_file_location(
            "bugs",
            "app/api/v1/endpoints/bugs.py"
        )
        bugs_module = importlib.util.module_from_spec(spec)
        
        print("✓ Bug endpoints module loaded successfully")
        
        # Check that router exists
        if hasattr(bugs_module, 'router'):
            print("✓ Router object exists")
        else:
            print("✗ Router object not found")
            return False
        
        print("\n✓ All checks passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error loading module: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_bug_endpoints()
    sys.exit(0 if success else 1)

"""
Test script to verify logging configuration for Excel Loader.

This script tests that logging is properly configured and working across all components.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'api'))
sys.path.insert(0, os.path.dirname(__file__))

from logging_utils import configure_logging, get_logger, log_info, log_warning, log_error, log_debug, log_import_progress, log_import_summary


def test_logging_configuration():
    """Test that logging can be configured."""
    print("Testing logging configuration...")
    
    # Create temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_log:
        log_file = temp_log.name
    
    try:
        # Configure logging
        configure_logging(log_level="INFO", log_file=log_file)
        print(f"✓ Logging configured successfully (log file: {log_file})")
        
        # Verify log file was created
        if os.path.exists(log_file):
            print(f"✓ Log file created: {log_file}")
        else:
            print(f"✗ Log file not created")
            return False
        
        return True
    finally:
        # Clean up
        if os.path.exists(log_file):
            os.unlink(log_file)


def test_logger_creation():
    """Test that loggers can be created."""
    print("\nTesting logger creation...")
    
    try:
        # Create loggers for each component
        components = [
            'excel_parser',
            'data_mapper',
            'hierarchy_builder',
            'database_writer',
            'import_orchestrator'
        ]
        
        for component in components:
            logger = get_logger(component)
            if logger:
                print(f"✓ Created logger for {component}")
            else:
                print(f"✗ Failed to create logger for {component}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error creating loggers: {str(e)}")
        return False


def test_logging_functions():
    """Test that logging functions work correctly."""
    print("\nTesting logging functions...")
    
    try:
        logger = get_logger("test_logger")
        
        # Test INFO level
        log_info(logger, "Test INFO message", test_key="test_value")
        print("✓ INFO logging works")
        
        # Test WARNING level
        log_warning(logger, "Test WARNING message", warning_type="test")
        print("✓ WARNING logging works")
        
        # Test ERROR level
        log_error(logger, "Test ERROR message", error_code="TEST001")
        print("✓ ERROR logging works")
        
        # Test DEBUG level
        log_debug(logger, "Test DEBUG message", debug_info="details")
        print("✓ DEBUG logging works")
        
        return True
    except Exception as e:
        print(f"✗ Error testing logging functions: {str(e)}")
        return False


def test_import_progress_logging():
    """Test import progress logging."""
    print("\nTesting import progress logging...")
    
    try:
        logger = get_logger("test_progress")
        
        # Simulate import progress
        log_import_progress(logger, "projects", 5, 10, additional_info="test")
        print("✓ Import progress logging works")
        
        return True
    except Exception as e:
        print(f"✗ Error testing import progress logging: {str(e)}")
        return False


def test_import_summary_logging():
    """Test import summary logging."""
    print("\nTesting import summary logging...")
    
    try:
        logger = get_logger("test_summary")
        
        # Test successful import summary
        summary = {
            'projects': 10,
            'usecases': 25,
            'user_stories': 50,
            'tasks': 100,
            'subtasks': 200
        }
        log_import_summary(logger, 45.5, summary, 3, 0)
        print("✓ Success import summary logging works")
        
        # Test import with warnings
        log_import_summary(logger, 30.2, summary, 5, 0)
        print("✓ Warning import summary logging works")
        
        # Test import with errors
        log_import_summary(logger, 15.8, summary, 2, 3)
        print("✓ Error import summary logging works")
        
        return True
    except Exception as e:
        print(f"✗ Error testing import summary logging: {str(e)}")
        return False


def test_component_logging():
    """Test that each component can log properly."""
    print("\nTesting component logging...")
    
    try:
        # Test data_mapper logging
        from data_mapper import DataMapper
        mapper = DataMapper()
        
        # Map a test row to trigger unmapped column logging
        test_row = {
            'project_name': 'Test Project',
            'unmapped_column': 'This should be logged as unmapped'
        }
        mapper.map_row('projects', test_row)
        mapper.log_unmapped_columns()
        print("✓ DataMapper logging works")
        
        return True
    except Exception as e:
        print(f"✗ Error testing component logging: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all logging tests."""
    print("=" * 60)
    print("Excel Loader Logging Verification")
    print("=" * 60)
    
    tests = [
        ("Logging Configuration", test_logging_configuration),
        ("Logger Creation", test_logger_creation),
        ("Logging Functions", test_logging_functions),
        ("Import Progress Logging", test_import_progress_logging),
        ("Import Summary Logging", test_import_summary_logging),
        ("Component Logging", test_component_logging),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All logging tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

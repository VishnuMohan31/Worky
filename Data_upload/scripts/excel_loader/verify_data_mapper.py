"""
Verification script for DataMapper component.
Tests all key functionality including column mapping, type conversion, and default values.
"""
import sys
from datetime import date, datetime
from data_mapper import DataMapper


def test_column_mapping():
    """Test basic column mapping functionality."""
    print("Testing column mapping...")
    mapper = DataMapper()
    
    # Test project mapping
    project_row = {
        'project_id': 'P001',
        'project_name': '  Test Project  ',  # With whitespace
        'descriptions': 'A test project',
        'client_name': 'Acme Corp',
        'status': 'Active',
    }
    
    mapped = mapper.map_row('projects', project_row)
    
    assert mapped['excel_id'] == 'P001', "Excel ID not mapped correctly"
    assert mapped['name'] == 'Test Project', "Name not trimmed correctly"
    assert mapped['short_description'] == 'A test project', "Description not mapped"
    assert mapped['_client_name'] == 'Acme Corp', "Client name not mapped"
    assert mapped['status'] == 'Active', "Status not mapped"
    
    print("✓ Column mapping works correctly")


def test_default_values():
    """Test default value application."""
    print("\nTesting default values...")
    mapper = DataMapper()
    
    # Test with minimal data
    task_row = {
        'task_id': 'T001',
        'title': 'Test Task',
    }
    
    mapped = mapper.map_row('tasks', task_row)
    
    assert mapped['status'] == 'To Do', "Default status not applied"
    assert mapped['priority'] == 'Medium', "Default priority not applied"
    assert mapped['short_description'] == '', "Default description not applied"
    
    print("✓ Default values applied correctly")


def test_date_conversion():
    """Test date conversion with various formats."""
    print("\nTesting date conversion...")
    mapper = DataMapper()
    
    # Test datetime object
    dt = datetime(2024, 1, 15, 10, 30)
    assert mapper.convert_date(dt) == date(2024, 1, 15), "Datetime conversion failed"
    
    # Test date object
    d = date(2024, 1, 15)
    assert mapper.convert_date(d) == date(2024, 1, 15), "Date object conversion failed"
    
    # Test ISO string
    assert mapper.convert_date('2024-01-15') == date(2024, 1, 15), "ISO string conversion failed"
    
    # Test US format
    assert mapper.convert_date('01/15/2024') == date(2024, 1, 15), "US format conversion failed"
    
    # Test European format
    assert mapper.convert_date('15/01/2024') == date(2024, 1, 15), "European format conversion failed"
    
    # Test Excel serial date (45000 = 2023-03-11)
    result = mapper.convert_date(45000)
    assert result is not None, "Excel serial date conversion failed"
    
    # Test None
    assert mapper.convert_date(None) is None, "None conversion failed"
    
    # Test empty string
    assert mapper.convert_date('') is None, "Empty string conversion failed"
    
    print("✓ Date conversion works correctly")


def test_number_conversion():
    """Test number conversion with various formats."""
    print("\nTesting number conversion...")
    mapper = DataMapper()
    
    # Test integer
    assert mapper.convert_number(42) == 42.0, "Integer conversion failed"
    
    # Test float
    assert mapper.convert_number(42.5) == 42.5, "Float conversion failed"
    
    # Test string number
    assert mapper.convert_number('42.5') == 42.5, "String number conversion failed"
    
    # Test number with commas
    assert mapper.convert_number('1,234.56') == 1234.56, "Comma number conversion failed"
    
    # Test number with currency
    assert mapper.convert_number('$1,234.56') == 1234.56, "Currency number conversion failed"
    
    # Test None
    assert mapper.convert_number(None) is None, "None conversion failed"
    
    # Test empty string
    assert mapper.convert_number('') is None, "Empty string conversion failed"
    
    print("✓ Number conversion works correctly")


def test_percentage_conversion():
    """Test percentage conversion."""
    print("\nTesting percentage conversion...")
    mapper = DataMapper()
    
    # Test percentage string
    assert mapper.convert_percentage('75%') == 0.75, "Percentage string conversion failed"
    
    # Test percentage with decimal
    assert mapper.convert_percentage('75.5%') == 0.755, "Decimal percentage conversion failed"
    
    # Test numeric percentage (assumes > 1 is percentage)
    assert mapper.convert_percentage(75) == 0.75, "Numeric percentage conversion failed"
    
    # Test decimal (< 1 stays as is)
    assert mapper.convert_percentage(0.75) == 0.75, "Decimal conversion failed"
    
    # Test None
    assert mapper.convert_percentage(None) is None, "None conversion failed"
    
    print("✓ Percentage conversion works correctly")


def test_unmapped_columns():
    """Test unmapped column tracking and logging."""
    print("\nTesting unmapped column tracking...")
    mapper = DataMapper()
    
    # Map row with extra columns
    project_row = {
        'project_id': 'P001',
        'project_name': 'Test Project',
        'extra_column_1': 'Should be ignored',
        'extra_column_2': 'Also ignored',
    }
    
    mapper.map_row('projects', project_row)
    
    report = mapper.get_unmapped_columns_report()
    assert 'projects' in report, "Unmapped columns not tracked"
    assert 'extra_column_1' in report['projects'], "Extra column 1 not tracked"
    assert 'extra_column_2' in report['projects'], "Extra column 2 not tracked"
    
    print("✓ Unmapped column tracking works correctly")


def test_all_entity_types():
    """Test mapping for all entity types."""
    print("\nTesting all entity types...")
    mapper = DataMapper()
    
    entity_types = ['projects', 'usecases', 'user_stories', 'tasks', 'subtasks']
    
    for entity_type in entity_types:
        # Create minimal row
        row = {'name': f'Test {entity_type}', 'title': f'Test {entity_type}'}
        
        try:
            mapped = mapper.map_row(entity_type, row)
            assert isinstance(mapped, dict), f"Mapping failed for {entity_type}"
            print(f"  ✓ {entity_type} mapping works")
        except Exception as e:
            print(f"  ✗ {entity_type} mapping failed: {e}")
            raise


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("DataMapper Component Verification")
    print("=" * 60)
    
    try:
        test_column_mapping()
        test_default_values()
        test_date_conversion()
        test_number_conversion()
        test_percentage_conversion()
        test_unmapped_columns()
        test_all_entity_types()
        
        print("\n" + "=" * 60)
        print("✓ All DataMapper tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

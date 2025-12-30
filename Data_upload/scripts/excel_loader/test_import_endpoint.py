"""
Test script for Excel Loader import endpoint.

This script demonstrates how to call the import endpoint programmatically.
"""

import requests
import sys
from pathlib import Path

def test_import_endpoint(file_path: str, base_url: str = "http://localhost:8001"):
    """
    Test the import endpoint with a file.
    
    Args:
        file_path: Path to the Excel file to import
        base_url: Base URL of the Excel Loader service
    """
    print("=" * 60)
    print("Testing Excel Loader Import Endpoint")
    print("=" * 60)
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"✗ Error: File not found: {file_path}")
        return False
    
    print(f"File: {file_path}")
    print(f"Service URL: {base_url}")
    
    # Check if service is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✓ Service is running")
        else:
            print(f"✗ Service health check failed: {health_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to service: {str(e)}")
        print("\nPlease start the service first:")
        print("  ./Data_upload/scripts/start_loader.sh")
        return False
    
    # Upload file
    print("\nUploading file...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(
                f"{base_url}/api/import",
                files=files,
                timeout=300  # 5 minutes timeout
            )
        
        print(f"Response status: {response.status_code}")
        
        # Parse response
        result = response.json()
        
        print("\n" + "=" * 60)
        print("Import Results")
        print("=" * 60)
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"Duration: {result.get('duration_seconds', 0):.2f}s")
        
        # Print summary
        summary = result.get('summary', {})
        if summary:
            print("\nSummary:")
            for entity_type, count in summary.items():
                print(f"  {entity_type}: {count}")
        
        # Print warnings
        warnings = result.get('warnings', [])
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for warning in warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more")
        
        # Print errors
        errors = result.get('errors', [])
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for error in errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
        
        print("=" * 60)
        
        return result.get('success', False)
        
    except requests.exceptions.Timeout:
        print("✗ Request timed out (import took longer than 5 minutes)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python test_import_endpoint.py <excel_file_path> [base_url]")
        print("\nExample:")
        print("  python test_import_endpoint.py ../../data/Project\\ Tracking\\ Automation.xlsx")
        print("  python test_import_endpoint.py /path/to/file.xlsx http://localhost:8001")
        sys.exit(1)
    
    file_path = sys.argv[1]
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8001"
    
    success = test_import_endpoint(file_path, base_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

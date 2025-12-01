#!/usr/bin/env python3
"""
Test script to import the actual Project Tracking Automation.xlsx file
"""

import requests
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:8001/api/import"
EXCEL_FILE = Path(__file__).parent.parent / "data" / "Project Tracking Automation.xlsx"

def test_import():
    """Test the import with the actual Excel file."""
    
    print(f"Testing import with file: {EXCEL_FILE}")
    print(f"File exists: {EXCEL_FILE.exists()}")
    print(f"File size: {EXCEL_FILE.stat().st_size / 1024:.2f} KB")
    print()
    
    if not EXCEL_FILE.exists():
        print(f"ERROR: File not found: {EXCEL_FILE}")
        return
    
    # Prepare the file upload
    with open(EXCEL_FILE, 'rb') as f:
        files = {'file': (EXCEL_FILE.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        print(f"Sending POST request to {API_URL}...")
        print()
        
        try:
            response = requests.post(API_URL, files=files, timeout=300)
            
            print(f"Response Status Code: {response.status_code}")
            print()
            
            # Parse response
            result = response.json()
            
            print("=" * 80)
            print("IMPORT RESULTS")
            print("=" * 80)
            print()
            
            print(f"Success: {result.get('success', False)}")
            print(f"Message: {result.get('message', 'N/A')}")
            print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")
            print()
            
            # Print summary
            summary = result.get('summary', {})
            if summary:
                print("Summary of Imported Records:")
                print("-" * 40)
                for entity_type, count in summary.items():
                    print(f"  {entity_type}: {count}")
                print()
                print(f"Total Records: {sum(summary.values())}")
                print()
            
            # Print warnings
            warnings = result.get('warnings', [])
            if warnings:
                print(f"Warnings ({len(warnings)}):")
                print("-" * 40)
                for i, warning in enumerate(warnings[:20], 1):  # Show first 20
                    print(f"  {i}. {warning}")
                if len(warnings) > 20:
                    print(f"  ... and {len(warnings) - 20} more warnings")
                print()
            
            # Print errors
            errors = result.get('errors', [])
            if errors:
                print(f"Errors ({len(errors)}):")
                print("-" * 40)
                for i, error in enumerate(errors[:20], 1):  # Show first 20
                    print(f"  {i}. {error}")
                if len(errors) > 20:
                    print(f"  ... and {len(errors) - 20} more errors")
                print()
            
            print("=" * 80)
            
            # Save full response to file
            output_file = Path(__file__).parent / "import_test_results.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nFull results saved to: {output_file}")
            
        except requests.exceptions.Timeout:
            print("ERROR: Request timed out after 300 seconds")
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to the API. Is the service running?")
        except Exception as e:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_import()

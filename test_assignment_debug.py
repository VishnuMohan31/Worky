#!/usr/bin/env python3
"""
Debug assignment creation issue
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8007/api/v1"

def test_assignment_creation():
    """Test assignment creation with the same data as the UI"""
    
    # Login first to get token
    login_data = {
        "email": "admin@datalegos.com",
        "password": "password"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test assignment data (same as UI sends)
    assignment_data = {
        "entity_type": "task",
        "entity_id": "TSK-000001",
        "user_id": "USR-001",  # Admin user
        "assignment_type": "developer"
    }
    
    print("Testing assignment creation with data:")
    print(json.dumps(assignment_data, indent=2))
    
    # Create assignment
    response = requests.post(
        f"{BASE_URL}/assignments/",
        json=assignment_data,
        headers=headers
    )
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 400:
        try:
            error_detail = response.json()
            print(f"\nDetailed error: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"\nRaw error response: {response.text}")

if __name__ == "__main__":
    test_assignment_creation()
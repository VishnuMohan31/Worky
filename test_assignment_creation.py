#!/usr/bin/env python3
"""
Test script to debug assignment creation issues
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8007/api/v1"

def test_assignment_creation():
    """Test assignment creation with various payloads"""
    
    # First, login to get token
    login_data = {
        "email": "admin@datalegos.com",
        "password": "password"
    }
    
    print("1. Testing login...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting available assignees first
    print("\n2. Testing available assignees...")
    assignees_response = requests.get(
        f"{BASE_URL}/assignments/available-assignees",
        params={"entity_type": "task", "entity_id": "TSK-000007"},
        headers=headers
    )
    print(f"Available assignees status: {assignees_response.status_code}")
    if assignees_response.status_code == 200:
        assignees = assignees_response.json()
        print(f"Found {len(assignees)} available assignees")
        if assignees:
            print(f"First assignee: {assignees[0]}")
    else:
        print(f"Available assignees error: {assignees_response.text}")
        return
    
    # Test assignment creation with different payloads
    test_payloads = [
        {
            "name": "Standard payload",
            "data": {
                "entity_type": "task",
                "entity_id": "TSK-000007",
                "user_id": "USR-001",
                "assignment_type": "developer"
            }
        },
        {
            "name": "Userstory payload with different user",
            "data": {
                "entity_type": "userstory",
                "entity_id": "UST-000003",
                "user_id": "USR-005",  # Alice Williams - DevOps
                "assignment_type": "owner"
            }
        }
    ]
    
    for test in test_payloads:
        print(f"\n3. Testing assignment creation - {test['name']}...")
        print(f"Payload: {json.dumps(test['data'], indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/assignments/",
            json=test['data'],
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Assignment created successfully!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ Assignment creation failed!")
            print(f"Error: {response.text}")
            
            # Try to get more details
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                pass

if __name__ == "__main__":
    test_assignment_creation()
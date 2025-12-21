#!/usr/bin/env python3
"""
Test script to verify assignment functionality is working correctly.
"""
import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8007"
LOGIN_EMAIL = "admin@datalegos.com"
LOGIN_PASSWORD = "password"

def login():
    """Login and get access token"""
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json={
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_assignment_operations():
    """Test assignment create, list, and delete operations"""
    token = login()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== Testing Assignment Operations ===")
    
    # 1. List current assignments
    print("\n1. Listing current assignments...")
    response = requests.get(f"{API_BASE_URL}/api/v1/assignments/", headers=headers)
    if response.status_code == 200:
        assignments = response.json()
        print(f"Found {len(assignments)} assignments:")
        for assignment in assignments:
            print(f"  - ID: {assignment['id']}, User: {assignment['user_name']}, Entity: {assignment['entity_type']}:{assignment['entity_id']}")
    else:
        print(f"Failed to list assignments: {response.status_code} - {response.text}")
        return
    
    # 2. Test assignment deletion if any exist
    if assignments:
        assignment_to_delete = assignments[0]
        print(f"\n2. Testing deletion of assignment: {assignment_to_delete['id']}")
        
        delete_response = requests.delete(f"{API_BASE_URL}/api/v1/assignments/{assignment_to_delete['id']}", headers=headers)
        if delete_response.status_code == 204:
            print("✅ Assignment deleted successfully!")
            
            # Verify it's gone
            list_response = requests.get(f"{API_BASE_URL}/api/v1/assignments/", headers=headers)
            if list_response.status_code == 200:
                remaining_assignments = list_response.json()
                if len(remaining_assignments) < len(assignments):
                    print("✅ Assignment successfully removed from list!")
                else:
                    print("❌ Assignment still appears in list!")
            else:
                print(f"Failed to verify deletion: {list_response.status_code}")
        else:
            print(f"❌ Failed to delete assignment: {delete_response.status_code} - {delete_response.text}")
    else:
        print("\n2. No assignments to test deletion with")
    
    # 3. Test available assignees
    print("\n3. Testing available assignees for a task...")
    response = requests.get(f"{API_BASE_URL}/api/v1/assignments/available-assignees", 
                          params={"entity_type": "task", "entity_id": "TSK-000001"}, 
                          headers=headers)
    if response.status_code == 200:
        assignees = response.json()
        print(f"Found {len(assignees)} available assignees:")
        for assignee in assignees:
            print(f"  - {assignee['full_name']} ({assignee['email']}) - Role: {assignee['role']}")
    else:
        print(f"Failed to get available assignees: {response.status_code} - {response.text}")
    
    # 4. Test creating a new assignment if we have assignees
    if response.status_code == 200 and assignees:
        assignee = assignees[0]
        print(f"\n4. Testing assignment creation for user: {assignee['full_name']}")
        
        create_response = requests.post(f"{API_BASE_URL}/api/v1/assignments/", 
                                      json={
                                          "entity_type": "task",
                                          "entity_id": "TSK-000001", 
                                          "user_id": assignee['id'],
                                          "assignment_type": "developer"
                                      }, 
                                      headers=headers)
        if create_response.status_code == 201:
            new_assignment = create_response.json()
            print(f"✅ Assignment created successfully! ID: {new_assignment['id']}")
        else:
            print(f"❌ Failed to create assignment: {create_response.status_code} - {create_response.text}")
    else:
        print("\n4. No assignees available to test assignment creation")

if __name__ == "__main__":
    test_assignment_operations()
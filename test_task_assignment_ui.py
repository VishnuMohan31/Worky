#!/usr/bin/env python3
"""
Test the task assignment functionality that's failing in the UI
"""
import requests
import json

BASE_URL = "http://localhost:8007/api/v1"

def test_task_assignment_ui():
    """Test the specific task assignment functionality from the UI perspective"""
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test the specific task from the screenshot: TSK-000007
    task_id = "TSK-000007"
    
    print(f"\n1. Testing available assignees for task {task_id}...")
    assignees_response = requests.get(
        f"{BASE_URL}/assignments/available-assignees",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    print(f"Status: {assignees_response.status_code}")
    if assignees_response.status_code == 200:
        assignees = assignees_response.json()
        print(f"✅ Found {len(assignees)} available assignees")
        for user in assignees:
            print(f"  - {user['full_name']} ({user['role']}) - Team member: {user['is_team_member']}")
    else:
        print(f"❌ Failed: {assignees_response.text}")
        return
    
    print(f"\n2. Checking current assignments for task {task_id}...")
    current_assignments_response = requests.get(
        f"{BASE_URL}/assignments/",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    print(f"Status: {current_assignments_response.status_code}")
    if current_assignments_response.status_code == 200:
        assignments = current_assignments_response.json()
        print(f"✅ Found {len(assignments)} current assignments")
        for assignment in assignments:
            print(f"  - {assignment['user_name']} ({assignment['assignment_type']}) - Active: {assignment['is_active']}")
            
            if assignment['is_active']:
                print(f"\n3. Testing assignment deletion (like UI does)...")
                delete_response = requests.delete(f"{BASE_URL}/assignments/{assignment['id']}", headers=headers)
                print(f"Delete status: {delete_response.status_code}")
                if delete_response.status_code not in [204, 200]:
                    print(f"❌ Delete failed: {delete_response.text}")
                else:
                    print("✅ Assignment deleted successfully")
    else:
        print(f"❌ Failed: {current_assignments_response.text}")
        return
    
    print(f"\n4. Testing new task assignment...")
    if assignees:
        # Try to assign to the first available user
        user_to_assign = assignees[0]
        print(f"Assigning to: {user_to_assign['full_name']} ({user_to_assign['role']})")
        
        assignment_data = {
            "entity_type": "task",
            "entity_id": task_id,
            "user_id": user_to_assign['id'],
            "assignment_type": "developer"
        }
        
        create_response = requests.post(f"{BASE_URL}/assignments/", json=assignment_data, headers=headers)
        print(f"Create status: {create_response.status_code}")
        
        if create_response.status_code == 201:
            result = create_response.json()
            print(f"✅ Assignment created successfully!")
            print(f"   Task: {result['entity_name']}")
            print(f"   Assigned to: {result['user_name']}")
            print(f"   Assignment ID: {result['id']}")
        else:
            print(f"❌ Assignment creation failed: {create_response.text}")
    
    print(f"\n5. Final check - listing assignments again...")
    final_check_response = requests.get(
        f"{BASE_URL}/assignments/",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    if final_check_response.status_code == 200:
        final_assignments = final_check_response.json()
        print(f"✅ Final count: {len(final_assignments)} assignments")
        for assignment in final_assignments:
            if assignment['is_active']:
                print(f"  - Active: {assignment['user_name']} ({assignment['assignment_type']})")
    
    print("\n🎯 Task Assignment UI Test Complete!")

if __name__ == "__main__":
    test_task_assignment_ui()
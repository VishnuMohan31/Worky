#!/usr/bin/env python3
"""
Simple test to check login and assignment functionality
"""
import requests
import json

API_BASE = "http://localhost:8007/api/v1"

def test_login_and_assignments():
    """Test login and assignment functionality"""
    
    # Login
    login_data = {
        "email": "testadmin@gmail.com",
        "password": "testadmin@123"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    result = response.json()
    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Get tasks
    response = requests.get(f"{API_BASE}/tasks", headers=headers)
    print(f"Tasks status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Failed to get tasks: {response.text}")
        return
    
    tasks = response.json()
    if not tasks:
        print("No tasks found")
        return
    
    task_id = tasks[0]["id"]
    print(f"Testing with task: {task_id}")
    
    # Get users
    response = requests.get(f"{API_BASE}/users", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get users: {response.text}")
        return
    
    users = response.json()
    if len(users) < 2:
        print("Need at least 2 users")
        return
    
    user1_id = users[0]["id"]
    user2_id = users[1]["id"]
    print(f"Users: {users[0]['full_name']}, {users[1]['full_name']}")
    
    # Clear existing assignments
    response = requests.get(f"{API_BASE}/assignments?entity_type=task&entity_id={task_id}", headers=headers)
    if response.status_code == 200:
        existing = response.json()
        for assignment in existing:
            if assignment["is_active"]:
                requests.delete(f"{API_BASE}/assignments/{assignment['id']}", headers=headers)
                print(f"Cleared assignment: {assignment['id']}")
    
    # Create first assignment
    assignment1_data = {
        "entity_type": "task",
        "entity_id": task_id,
        "user_id": user1_id,
        "assignment_type": "developer"
    }
    
    response = requests.post(f"{API_BASE}/assignments", json=assignment1_data, headers=headers)
    print(f"First assignment status: {response.status_code}")
    if response.status_code == 201:
        result1 = response.json()
        print(f"✅ First assignment created: {result1['id']}")
    else:
        print(f"❌ First assignment failed: {response.text}")
        return
    
    # Create second assignment
    assignment2_data = {
        "entity_type": "task",
        "entity_id": task_id,
        "user_id": user2_id,
        "assignment_type": "developer"
    }
    
    response = requests.post(f"{API_BASE}/assignments", json=assignment2_data, headers=headers)
    print(f"Second assignment status: {response.status_code}")
    if response.status_code == 201:
        result2 = response.json()
        print(f"✅ Second assignment created: {result2['id']}")
    else:
        print(f"❌ Second assignment failed: {response.text}")
        return
    
    # Verify both assignments exist
    response = requests.get(f"{API_BASE}/assignments?entity_type=task&entity_id={task_id}", headers=headers)
    if response.status_code == 200:
        assignments = response.json()
        active_assignments = [a for a in assignments if a["is_active"]]
        print(f"\n📊 Total active assignments: {len(active_assignments)}")
        
        for assignment in active_assignments:
            print(f"  - {assignment['user_name']} ({assignment['assignment_type']})")
        
        if len(active_assignments) >= 2:
            print("✅ SUCCESS: Multiple assignments working correctly!")
        else:
            print("❌ FAILURE: Multiple assignments not working")
    else:
        print(f"❌ Failed to verify assignments: {response.text}")

if __name__ == "__main__":
    test_login_and_assignments()
#!/usr/bin/env python3
"""
Final test of assignment system with proper role and team membership
"""
import requests
import json

BASE_URL = "http://localhost:8007/api/v1"

def test_final_assignment():
    """Test assignment with proper validation"""
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Test 1: Remove existing assignment first
    print("\n1. Checking existing assignments for UST-000003...")
    existing_assignments = requests.get(
        f"{BASE_URL}/assignments/",
        params={"entity_type": "userstory", "entity_id": "UST-000003"},
        headers=headers
    )
    
    if existing_assignments.status_code == 200:
        assignments = existing_assignments.json()
        print(f"Found {len(assignments)} existing assignments")
        
        for assignment in assignments:
            if assignment['is_active']:
                print(f"Removing existing assignment: {assignment['id']} ({assignment['user_name']})")
                delete_response = requests.delete(f"{BASE_URL}/assignments/{assignment['id']}", headers=headers)
                print(f"Delete status: {delete_response.status_code}")
    
    # Test 2: Create new assignment with Admin user (who is now a team member)
    print("\n2. Creating new userstory assignment with Admin user...")
    assignment_data = {
        "entity_type": "userstory",
        "entity_id": "UST-000003",
        "user_id": "USR-001",  # Admin user
        "assignment_type": "owner"
    }
    
    assignment_response = requests.post(
        f"{BASE_URL}/assignments/",
        json=assignment_data,
        headers=headers
    )
    
    print(f"Assignment status: {assignment_response.status_code}")
    if assignment_response.status_code == 201:
        print("✅ Userstory assignment successful!")
        result = assignment_response.json()
        print(f"Assigned {result['entity_name']} to {result['user_name']} as {result['assignment_type']}")
    else:
        print("❌ Userstory assignment failed!")
        print(f"Error: {assignment_response.text}")
    
    # Test 3: Test task assignment with a developer
    print("\n3. Testing task assignment with developer role...")
    
    # Get available assignees for task
    task_assignees = requests.get(
        f"{BASE_URL}/assignments/available-assignees",
        params={"entity_type": "task", "entity_id": "TSK-000007"},
        headers=headers
    )
    
    if task_assignees.status_code == 200:
        assignees = task_assignees.json()
        developer_users = [u for u in assignees if u['role'] in ['Developer', 'Admin']]
        
        if developer_users:
            test_user = developer_users[0]
            print(f"Testing with {test_user['full_name']} ({test_user['role']})")
            
            # Remove existing task assignment first
            existing_task_assignments = requests.get(
                f"{BASE_URL}/assignments/",
                params={"entity_type": "task", "entity_id": "TSK-000007"},
                headers=headers
            )
            
            if existing_task_assignments.status_code == 200:
                task_assignments = existing_task_assignments.json()
                for assignment in task_assignments:
                    if assignment['is_active']:
                        print(f"Removing existing task assignment: {assignment['id']}")
                        requests.delete(f"{BASE_URL}/assignments/{assignment['id']}", headers=headers)
            
            # Create new task assignment
            task_assignment_data = {
                "entity_type": "task",
                "entity_id": "TSK-000007",
                "user_id": test_user['id'],
                "assignment_type": "developer"
            }
            
            task_assignment_response = requests.post(
                f"{BASE_URL}/assignments/",
                json=task_assignment_data,
                headers=headers
            )
            
            print(f"Task assignment status: {task_assignment_response.status_code}")
            if task_assignment_response.status_code == 201:
                print("✅ Task assignment successful!")
                result = task_assignment_response.json()
                print(f"Assigned {result['entity_name']} to {result['user_name']} as {result['assignment_type']}")
            else:
                print("❌ Task assignment failed!")
                print(f"Error: {task_assignment_response.text}")
    
    print("\n🎉 Assignment system testing complete!")

if __name__ == "__main__":
    test_final_assignment()
#!/usr/bin/env python3
"""
Simple Assignment Test - Test assignment creation and check database state
"""
import requests
import json

def test_assignment():
    base_url = "http://localhost:8007/api/v1"
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("Login failed")
        return
        
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get a task to assign
    tasks_response = requests.get(f"{base_url}/tasks/", headers=headers)
    if tasks_response.status_code != 200:
        print("Failed to get tasks")
        return
        
    tasks = tasks_response.json()
    if not tasks:
        print("No tasks found")
        return
        
    task_id = tasks[0]["id"]
    print(f"Using task: {task_id}")
    
    # Get available assignees
    assignees_response = requests.get(
        f"{base_url}/assignments/available-assignees",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    if assignees_response.status_code != 200:
        print("Failed to get assignees")
        return
        
    assignees = assignees_response.json()
    if not assignees:
        print("No assignees found")
        return
        
    user_id = assignees[0]["id"]
    print(f"Using assignee: {assignees[0]['full_name']} ({user_id})")
    
    # Check existing assignments before
    before_response = requests.get(
        f"{base_url}/assignments/",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    before_count = 0
    if before_response.status_code == 200:
        before_assignments = before_response.json()
        before_count = len([a for a in before_assignments if a["is_active"]])
        print(f"Assignments before: {before_count}")
    
    # Try to create assignment
    assignment_data = {
        "entity_type": "task",
        "entity_id": task_id,
        "user_id": user_id,
        "assignment_type": "developer"
    }
    
    print(f"Creating assignment: {assignment_data}")
    response = requests.post(f"{base_url}/assignments/", json=assignment_data, headers=headers)
    
    print(f"Assignment creation response: {response.status_code}")
    if response.status_code != 201:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
    
    # Check assignments after
    after_response = requests.get(
        f"{base_url}/assignments/",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    if after_response.status_code == 200:
        after_assignments = after_response.json()
        after_count = len([a for a in after_assignments if a["is_active"]])
        print(f"Assignments after: {after_count}")
        
        if after_count > before_count:
            print("✅ Assignment was actually created in database despite error!")
            # Show the assignment
            for assignment in after_assignments:
                if assignment["is_active"] and assignment["user_id"] == user_id:
                    print(f"   Assignment ID: {assignment['id']}")
                    print(f"   User: {assignment['user_name']}")
                    print(f"   Type: {assignment['assignment_type']}")
        else:
            print("❌ Assignment was not created")
    else:
        print("Failed to check assignments after")

if __name__ == "__main__":
    test_assignment()
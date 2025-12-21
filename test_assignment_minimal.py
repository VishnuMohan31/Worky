#!/usr/bin/env python3
"""
Minimal assignment test to isolate the async context error
"""
import requests
import json

def test_minimal_assignment():
    """Test minimal assignment creation"""
    base_url = "http://localhost:8007/api/v1"
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, let's see what assignments exist
    all_assignments_response = requests.get(f"{base_url}/assignments/", headers=headers)
    if all_assignments_response.status_code == 200:
        all_assignments = all_assignments_response.json()
        print(f"Found {len(all_assignments)} existing assignments")
        for assignment in all_assignments[:5]:  # Show first 5
            print(f"  - {assignment['entity_type']} {assignment['entity_id']} -> {assignment['user_name']} ({assignment['assignment_type']})")
    
    # Clean up existing assignments for testing
    if all_assignments_response.status_code == 200:
        all_assignments = all_assignments_response.json()
        task_assignments = [a for a in all_assignments if a['entity_type'] == 'task' and a['is_active']]
        if task_assignments:
            print(f"Cleaning up {len(task_assignments)} task assignments...")
            for assignment in task_assignments[:3]:  # Clean up first 3
                delete_response = requests.delete(f"{base_url}/assignments/{assignment['id']}", headers=headers)
                print(f"  Deleted assignment {assignment['id']}: {delete_response.status_code}")
    
    # Get a task to assign to
    tasks_response = requests.get(f"{base_url}/tasks/", headers=headers)
    if tasks_response.status_code != 200:
        print(f"Failed to get tasks: {tasks_response.status_code}")
        return False
    
    tasks = tasks_response.json()
    if not tasks:
        print("No tasks found")
        return False
    
    # Find a task without existing assignments
    task_id = None
    for task in tasks:
        # Check if task has existing assignments
        assignments_response = requests.get(
            f"{base_url}/assignments/",
            params={"entity_type": "task", "entity_id": task["id"], "is_active": True},
            headers=headers
        )
        if assignments_response.status_code == 200:
            assignments = assignments_response.json()
            if not assignments:  # No existing assignments
                task_id = task["id"]
                break
    
    if not task_id:
        print("No unassigned tasks found")
        return False
    
    print(f"Using unassigned task: {task_id}")
    
    # Get available assignees
    assignees_response = requests.get(
        f"{base_url}/assignments/available-assignees",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    if assignees_response.status_code != 200:
        print(f"Failed to get assignees: {assignees_response.status_code}")
        return False
    
    assignees = assignees_response.json()
    if not assignees:
        print("No assignees found")
        return False
    
    # Find a non-admin assignee
    assignee = None
    for a in assignees:
        if a.get("email") != "admin@datalegos.com":
            assignee = a
            break
    
    if not assignee:
        print("No non-admin assignee found")
        return False
    
    print(f"Using assignee: {assignee['full_name']} ({assignee['email']})")
    
    # Create assignment
    assignment_data = {
        "entity_type": "task",
        "entity_id": task_id,
        "user_id": assignee["id"],
        "assignment_type": "developer"
    }
    
    print(f"Creating assignment: {assignment_data}")
    
    response = requests.post(f"{base_url}/assignments/", json=assignment_data, headers=headers)
    
    print(f"Assignment response: {response.status_code}")
    if response.status_code != 201:
        print(f"Assignment failed: {response.text}")
        return False
    
    assignment = response.json()
    print(f"Assignment created: {assignment['id']}")
    
    # Clean up - delete assignment
    delete_response = requests.delete(f"{base_url}/assignments/{assignment['id']}", headers=headers)
    print(f"Delete response: {delete_response.status_code}")
    
    return True

if __name__ == "__main__":
    success = test_minimal_assignment()
    if success:
        print("✅ Minimal assignment test passed")
    else:
        print("❌ Minimal assignment test failed")
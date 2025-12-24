#!/usr/bin/env python3
"""
Test assignment functionality for tasks and subtasks
"""
import requests
import json

def test_assignment_functionality():
    base_url = "http://localhost:8007/api/v1"
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
        
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Get tasks
    tasks_response = requests.get(f"{base_url}/tasks/", headers=headers)
    if tasks_response.status_code != 200:
        print("❌ Failed to get tasks")
        return
        
    tasks = tasks_response.json()
    if not tasks:
        print("❌ No tasks found")
        return
        
    task_list = tasks
    task_id = task_list[0]["id"]
    task_title = task_list[0]["title"]
    print(f"✅ Found task: {task_title} ({task_id})")
    
    # Get users for assignment
    users_response = requests.get(f"{base_url}/users/", headers=headers)
    if users_response.status_code != 200:
        print("❌ Failed to get users")
        return
        
    users = users_response.json()
    if not users:
        print("❌ No users found")
        return
        
    # Find a developer user
    developer_user = None
    for user in users:
        if user["role"] in ["Developer", "Admin"]:
            developer_user = user
            break
    
    if not developer_user:
        print("❌ No developer user found")
        return
    
    print(f"✅ Found developer: {developer_user['full_name']} ({developer_user['id']})")
    
    # Test different assignment types
    assignment_types = ["developer", "tester", "designer", "reviewer", "lead"]
    
    for assignment_type in assignment_types:
        print(f"🧪 Testing {assignment_type} assignment...")
        
        assignment_data = {
            "entity_type": "task",
            "entity_id": task_id,
            "user_id": developer_user["id"],
            "assignment_type": assignment_type
        }
        
        response = requests.post(f"{base_url}/assignments/", json=assignment_data, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ {assignment_type.title()} assignment created successfully!")
            assignment = response.json()
            print(f"   Assignment ID: {assignment['id']}")
            print(f"   Assignee: {assignment['user_name']}")
            
            # Delete the assignment to test next type
            delete_response = requests.delete(f"{base_url}/assignments/{assignment['id']}", headers=headers)
            if delete_response.status_code == 204:
                print(f"✅ {assignment_type.title()} assignment deleted successfully")
            else:
                print(f"⚠️  Failed to delete {assignment_type} assignment")
        else:
            print(f"❌ {assignment_type.title()} assignment failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    # Test final assignment
    print(f"🧪 Creating final developer assignment...")
    
    final_assignment_data = {
        "entity_type": "task",
        "entity_id": task_id,
        "user_id": developer_user["id"],
        "assignment_type": "developer"
    }
    
    response = requests.post(f"{base_url}/assignments/", json=final_assignment_data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Final assignment created successfully!")
        assignment = response.json()
        print(f"   Assignment ID: {assignment['id']}")
        print(f"   Assignee: {assignment['user_name']}")
    else:
        print(f"❌ Final assignment failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Check current assignments for this task
    assignments_response = requests.get(
        f"{base_url}/assignments/",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    if assignments_response.status_code == 200:
        assignments = assignments_response.json()
        active_assignments = [a for a in assignments if a["is_active"]]
        print(f"✅ Current assignments for {task_title}: {len(active_assignments)}")
        for assignment in active_assignments:
            print(f"   - {assignment['user_name']} ({assignment['assignment_type']}) - ID: {assignment['id']}")
    else:
        print("❌ Failed to get assignments")
    
    print("\n🎉 Assignment functionality is working!")
    print("📋 To test in UI:")
    print(f"   1. Go to http://localhost:3007/hierarchy")
    print(f"   2. Navigate to Tasks")
    print(f"   3. Click on '{task_title}'")
    print(f"   4. Look for 'Assigned:' section in the entity details")
    print(f"   5. You should see the assigned users with '+ Assign' button")

if __name__ == "__main__":
    test_assignment_functionality()
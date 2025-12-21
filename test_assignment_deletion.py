#!/usr/bin/env python3
"""
Test assignment deletion functionality specifically
"""
import requests
import json

BASE_URL = "http://localhost:8007/api/v1"

def test_assignment_deletion():
    """Test the assignment deletion that's failing in the UI"""
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test with the task from the screenshot
    task_id = "TSK-000007"
    
    print(f"\n1. Getting current assignments for task {task_id}...")
    assignments_response = requests.get(
        f"{BASE_URL}/assignments/",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    if assignments_response.status_code != 200:
        print(f"❌ Failed to get assignments: {assignments_response.text}")
        return
    
    assignments = assignments_response.json()
    active_assignments = [a for a in assignments if a['is_active']]
    
    print(f"✅ Found {len(assignments)} total assignments, {len(active_assignments)} active")
    
    if not active_assignments:
        print("ℹ️  No active assignments to delete. Creating one first...")
        
        # Get available assignees
        assignees_response = requests.get(
            f"{BASE_URL}/assignments/available-assignees",
            params={"entity_type": "task", "entity_id": task_id},
            headers=headers
        )
        
        if assignees_response.status_code == 200:
            assignees = assignees_response.json()
            if assignees:
                # Create an assignment
                assignment_data = {
                    "entity_type": "task",
                    "entity_id": task_id,
                    "user_id": assignees[0]['id'],
                    "assignment_type": "developer"
                }
                
                create_response = requests.post(f"{BASE_URL}/assignments/", json=assignment_data, headers=headers)
                if create_response.status_code == 201:
                    new_assignment = create_response.json()
                    active_assignments = [new_assignment]
                    print(f"✅ Created test assignment: {new_assignment['id']}")
                else:
                    print(f"❌ Failed to create test assignment: {create_response.text}")
                    return
    
    # Test deletion of each active assignment
    for assignment in active_assignments:
        assignment_id = assignment['id']
        user_name = assignment['user_name']
        
        print(f"\n2. Testing deletion of assignment {assignment_id} ({user_name})...")
        
        delete_response = requests.delete(f"{BASE_URL}/assignments/{assignment_id}", headers=headers)
        
        print(f"Delete status: {delete_response.status_code}")
        
        if delete_response.status_code == 204:
            print(f"✅ Assignment {assignment_id} deleted successfully")
            
            # Verify it's actually deleted
            verify_response = requests.get(
                f"{BASE_URL}/assignments/",
                params={"entity_type": "task", "entity_id": task_id},
                headers=headers
            )
            
            if verify_response.status_code == 200:
                updated_assignments = verify_response.json()
                still_active = [a for a in updated_assignments if a['id'] == assignment_id and a['is_active']]
                
                if not still_active:
                    print(f"✅ Verified: Assignment {assignment_id} is no longer active")
                else:
                    print(f"❌ Assignment {assignment_id} is still active after deletion")
            
        elif delete_response.status_code == 404:
            print(f"❌ Assignment {assignment_id} not found (404 error)")
            print(f"Response: {delete_response.text}")
        elif delete_response.status_code == 500:
            print(f"❌ Server error deleting assignment {assignment_id}")
            print(f"Response: {delete_response.text}")
        else:
            print(f"❌ Unexpected status {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
    
    print(f"\n3. Final verification - checking all assignments...")
    final_response = requests.get(
        f"{BASE_URL}/assignments/",
        params={"entity_type": "task", "entity_id": task_id},
        headers=headers
    )
    
    if final_response.status_code == 200:
        final_assignments = final_response.json()
        final_active = [a for a in final_assignments if a['is_active']]
        print(f"✅ Final state: {len(final_assignments)} total assignments, {len(final_active)} active")
        
        for assignment in final_active:
            print(f"  - Active: {assignment['user_name']} ({assignment['id']})")
    
    print("\n🎯 Assignment Deletion Test Complete!")

if __name__ == "__main__":
    test_assignment_deletion()
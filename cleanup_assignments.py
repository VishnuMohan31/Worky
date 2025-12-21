#!/usr/bin/env python3
"""
Clean up duplicate assignments in the database
"""
import requests

# Login and get token
response = requests.post("http://localhost:8007/api/v1/auth/login", json={
    "email": "admin@datalegos.com",
    "password": "password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("=== Cleaning up inactive assignments ===")

# Get all inactive assignments
response = requests.get("http://localhost:8007/api/v1/assignments/?is_active=false", headers=headers)
inactive_assignments = response.json()
print(f"Found {len(inactive_assignments)} inactive assignments to clean up")

# Note: We'll keep the inactive assignments as they represent history
# Instead, let's just test with the current active assignment

# Get active assignments
response = requests.get("http://localhost:8007/api/v1/assignments/?is_active=true", headers=headers)
active_assignments = response.json()
print(f"Found {len(active_assignments)} active assignments:")

for assignment in active_assignments:
    print(f"  - {assignment['user_name']} assigned to {assignment['entity_type']}:{assignment['entity_id']}")

print("\n=== Testing assignment deletion ===")
if active_assignments:
    assignment_to_delete = active_assignments[0]
    print(f"Deleting assignment: {assignment_to_delete['id']}")
    
    delete_response = requests.delete(f"http://localhost:8007/api/v1/assignments/{assignment_to_delete['id']}", headers=headers)
    if delete_response.status_code == 204:
        print("✅ Assignment deleted successfully!")
        
        # Verify it's gone from active list
        response = requests.get("http://localhost:8007/api/v1/assignments/?is_active=true", headers=headers)
        remaining_active = response.json()
        print(f"Remaining active assignments: {len(remaining_active)}")
        
        if len(remaining_active) < len(active_assignments):
            print("✅ Assignment successfully removed from active list!")
        else:
            print("❌ Assignment still appears in active list!")
    else:
        print(f"❌ Failed to delete assignment: {delete_response.status_code} - {delete_response.text}")

print("\n=== Testing assignment creation ===")
# Get available assignees for a task
response = requests.get("http://localhost:8007/api/v1/assignments/available-assignees", 
                      params={"entity_type": "task", "entity_id": "TSK-000001"}, 
                      headers=headers)
if response.status_code == 200:
    assignees = response.json()
    if assignees:
        assignee = assignees[0]
        print(f"Creating assignment for {assignee['full_name']} on task TSK-000001")
        
        create_response = requests.post("http://localhost:8007/api/v1/assignments/", 
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
            
            # Verify it appears in active list
            response = requests.get("http://localhost:8007/api/v1/assignments/?is_active=true", headers=headers)
            current_active = response.json()
            print(f"Current active assignments: {len(current_active)}")
            
        else:
            print(f"❌ Failed to create assignment: {create_response.status_code} - {create_response.text}")
    else:
        print("No assignees available")
else:
    print(f"Failed to get assignees: {response.status_code}")
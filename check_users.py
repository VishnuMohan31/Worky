#!/usr/bin/env python3
import requests

# Login and get token
response = requests.post("http://localhost:8007/api/v1/auth/login", json={
    "email": "admin@datalegos.com",
    "password": "password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get all users
response = requests.get("http://localhost:8007/api/v1/users/", headers=headers)
if response.status_code == 200:
    users = response.json()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  - {user['id']}: {user['full_name']} ({user['email']}) - Role: {user.get('role', 'No role')} - Active: {user.get('is_active', 'Unknown')}")
else:
    print(f"Failed to get users: {response.status_code}")

# Get available assignees for the task
print(f"\n=== Available assignees for task TSK-000001 ===")
response = requests.get("http://localhost:8007/api/v1/assignments/available-assignees", 
                      params={"entity_type": "task", "entity_id": "TSK-000001"}, 
                      headers=headers)
if response.status_code == 200:
    assignees = response.json()
    print(f"Found {len(assignees)} available assignees:")
    for assignee in assignees:
        print(f"  - {assignee['id']}: {assignee['full_name']} ({assignee['email']}) - Role: {assignee['role']}")
else:
    print(f"Failed to get assignees: {response.status_code}")
#!/usr/bin/env python3
"""
Minimal assignment creation test to isolate the database issue
"""
import requests

# Login and get token
response = requests.post("http://localhost:8007/api/v1/auth/login", json={
    "email": "admin@datalegos.com",
    "password": "password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("=== Testing minimal assignment creation ===")

# Try to create assignment with minimal data
assignment_data = {
    "entity_type": "task",
    "entity_id": "TSK-000007",
    "user_id": "USR-005",  # Alice Williams
    "assignment_type": "developer"
}

print(f"Creating assignment: {assignment_data}")

response = requests.post("http://localhost:8007/api/v1/assignments/", 
                        json=assignment_data, 
                        headers=headers)

print(f"Response status: {response.status_code}")
print(f"Response body: {response.text}")

if response.status_code == 201:
    print("✅ Assignment created successfully!")
    assignment = response.json()
    print(f"Assignment ID: {assignment['id']}")
else:
    print(f"❌ Assignment creation failed: {response.status_code}")
    
    # Let's also test if the user exists
    print("\n=== Checking if user exists ===")
    user_response = requests.get("http://localhost:8007/api/v1/users/", headers=headers)
    if user_response.status_code == 200:
        users = user_response.json()
        alice_user = next((u for u in users if u['id'] == 'USR-005'), None)
        if alice_user:
            print(f"✅ User found: {alice_user['full_name']} ({alice_user['email']})")
        else:
            print("❌ User USR-005 not found")
    
    # Let's also check if the task exists
    print("\n=== Checking if task exists ===")
    task_response = requests.get("http://localhost:8007/api/v1/tasks/TSK-000007", headers=headers)
    if task_response.status_code == 200:
        task = task_response.json()
        print(f"✅ Task found: {task.get('title', 'No title')}")
    else:
        print(f"❌ Task TSK-000007 not found: {task_response.status_code}")
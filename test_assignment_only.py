#!/usr/bin/env python3
import requests

# Login and get token
response = requests.post("http://localhost:8007/api/v1/auth/login", json={
    "email": "admin@datalegos.com",
    "password": "password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create assignment
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
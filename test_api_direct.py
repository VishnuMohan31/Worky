#!/usr/bin/env python3
import requests

# Login and get token
response = requests.post("http://localhost:8007/api/v1/auth/login", json={
    "email": "admin@datalegos.com",
    "password": "password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test assignments with is_active=true
print("=== Testing assignments with is_active=true ===")
response = requests.get("http://localhost:8007/api/v1/assignments/?is_active=true", headers=headers)
assignments = response.json()
print(f"Found {len(assignments)} active assignments")

# Test assignments with is_active=false  
print("\n=== Testing assignments with is_active=false ===")
response = requests.get("http://localhost:8007/api/v1/assignments/?is_active=false", headers=headers)
assignments = response.json()
print(f"Found {len(assignments)} inactive assignments")

# Test assignments with no filter (should default to active only)
print("\n=== Testing assignments with no filter (should be active only) ===")
response = requests.get("http://localhost:8007/api/v1/assignments/", headers=headers)
assignments = response.json()
print(f"Found {len(assignments)} assignments (should be active only)")
for assignment in assignments[:3]:  # Show first 3
    print(f"  - {assignment['id']}: is_active = {assignment.get('is_active', 'missing')}")
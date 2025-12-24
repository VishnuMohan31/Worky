#!/usr/bin/env python3
"""
Test ownership functionality
"""
import requests
import json

def test_ownership():
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
    
    # Get clients
    clients_response = requests.get(f"{base_url}/clients/", headers=headers)
    if clients_response.status_code != 200:
        print("❌ Failed to get clients")
        return
        
    clients = clients_response.json()
    if not clients.get("clients"):
        print("❌ No clients found")
        return
        
    client_list = clients["clients"]
    client_id = client_list[0]["id"]
    client_name = client_list[0]["name"]
    print(f"✅ Found client: {client_name} ({client_id})")
    
    # Get users for ownership
    users_response = requests.get(f"{base_url}/users/", headers=headers)
    if users_response.status_code != 200:
        print("❌ Failed to get users")
        return
        
    users = users_response.json()
    if not users:
        print("❌ No users found")
        return
        
    user_id = None
    user_name = None
    
    # Find an admin user
    for user in users:
        if user["role"] == "Admin":
            user_id = user["id"]
            user_name = user["full_name"]
            break
    
    if not user_id:
        # Fallback to first user
        user_id = users[0]["id"]
        user_name = users[0]["full_name"]
    print(f"✅ Found user: {user_name} ({user_id})")
    
    # Test ownership assignment
    ownership_data = {
        "entity_type": "client",
        "entity_id": client_id,
        "user_id": user_id,
        "assignment_type": "owner"
    }
    
    print(f"🧪 Testing ownership assignment...")
    response = requests.post(f"{base_url}/assignments/", json=ownership_data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Ownership assignment created successfully!")
        assignment = response.json()
        print(f"   Assignment ID: {assignment['id']}")
        print(f"   Owner: {assignment['user_name']}")
    else:
        print(f"❌ Ownership assignment failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Check existing assignments for this client
    assignments_response = requests.get(
        f"{base_url}/assignments/",
        params={"entity_type": "client", "entity_id": client_id},
        headers=headers
    )
    
    if assignments_response.status_code == 200:
        assignments = assignments_response.json()
        owner_assignments = [a for a in assignments if a["assignment_type"] == "owner" and a["is_active"]]
        print(f"✅ Current owners for {client_name}: {len(owner_assignments)}")
        for assignment in owner_assignments:
            print(f"   - {assignment['user_name']} (ID: {assignment['id']})")
    else:
        print("❌ Failed to get assignments")

if __name__ == "__main__":
    test_ownership()
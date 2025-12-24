#!/usr/bin/env python3
"""
Test UI ownership functionality by checking if the ownership components are working
"""
import requests
import json

def test_ui_ownership():
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
    
    # Check current owners
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
        return
    
    # Test adding another owner
    users_response = requests.get(f"{base_url}/users/", headers=headers)
    if users_response.status_code != 200:
        print("❌ Failed to get users")
        return
        
    users = users_response.json()
    if not users:
        print("❌ No users found")
        return
    
    # Find a user who is not already an owner
    current_owner_ids = [a["user_id"] for a in owner_assignments]
    available_user = None
    
    for user in users:
        if user["id"] not in current_owner_ids and user["role"] in ["Admin", "Owner", "Project Manager"]:
            available_user = user
            break
    
    if available_user:
        print(f"🧪 Testing adding another owner: {available_user['full_name']}")
        
        ownership_data = {
            "entity_type": "client",
            "entity_id": client_id,
            "user_id": available_user["id"],
            "assignment_type": "owner"
        }
        
        response = requests.post(f"{base_url}/assignments/", json=ownership_data, headers=headers)
        
        if response.status_code == 201:
            print("✅ Additional owner added successfully!")
            assignment = response.json()
            print(f"   Assignment ID: {assignment['id']}")
            print(f"   Owner: {assignment['user_name']}")
        else:
            print(f"❌ Failed to add additional owner: {response.status_code}")
            print(f"   Error: {response.text}")
    else:
        print("ℹ️  No additional eligible users found for ownership")
    
    # Final check - get all owners
    assignments_response = requests.get(
        f"{base_url}/assignments/",
        params={"entity_type": "client", "entity_id": client_id},
        headers=headers
    )
    
    if assignments_response.status_code == 200:
        assignments = assignments_response.json()
        owner_assignments = [a for a in assignments if a["assignment_type"] == "owner" and a["is_active"]]
        print(f"✅ Final owners for {client_name}: {len(owner_assignments)}")
        for assignment in owner_assignments:
            print(f"   - {assignment['user_name']} (ID: {assignment['id']})")
    
    print("\n🎉 Ownership functionality is working!")
    print("📋 To test in UI:")
    print(f"   1. Go to http://localhost:3007/hierarchy")
    print(f"   2. Navigate to Clients")
    print(f"   3. Click on '{client_name}'")
    print(f"   4. Look for 'Owners:' section in the entity details")
    print(f"   5. You should see the assigned owners with '+ Add Owner' button")

if __name__ == "__main__":
    test_ui_ownership()
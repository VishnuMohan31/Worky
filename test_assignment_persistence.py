#!/usr/bin/env python3
"""
Test Assignment Persistence
Verify that assignments persist correctly when adding multiple assignees
"""

import requests
import json

def test_assignment_persistence():
    print("🔧 TESTING ASSIGNMENT PERSISTENCE")
    print("=" * 50)
    
    base_url = "http://localhost:8007/api/v1"
    
    # Login to get token
    login_data = {
        "email": "admin@datalegos.com",
        "password": "password"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ Login successful")
        
        # Find a user story to test with
        userstories_response = requests.get(f"{base_url}/user-stories/", headers=headers)
        if userstories_response.status_code != 200:
            print(f"❌ Failed to get user stories: {userstories_response.status_code}")
            return
        
        userstories = userstories_response.json()
        if not userstories:
            print("❌ No user stories found")
            return
        
        test_userstory = userstories[0]
        userstory_id = test_userstory["id"]
        print(f"✅ Using user story: {test_userstory['title']} (ID: {userstory_id})")
        
        # Get all users
        users_response = requests.get(f"{base_url}/users/", headers=headers)
        if users_response.status_code != 200:
            print(f"❌ Failed to get users: {users_response.status_code}")
            return
        
        users = users_response.json()
        if len(users) < 2:
            print("❌ Need at least 2 users for testing")
            return
        
        print(f"✅ Found {len(users)} users")
        
        # Clear existing assignments for this user story
        print("\n🧹 Clearing existing assignments...")
        assignments_response = requests.get(
            f"{base_url}/assignments/", 
            headers=headers,
            params={"entity_type": "userstory", "entity_id": userstory_id}
        )
        
        if assignments_response.status_code == 200:
            existing_assignments = assignments_response.json()
            for assignment in existing_assignments:
                if assignment.get("is_active"):
                    delete_response = requests.delete(
                        f"{base_url}/assignments/{assignment['id']}", 
                        headers=headers
                    )
                    if delete_response.status_code == 200:
                        print(f"  ✅ Deleted assignment {assignment['id']}")
                    else:
                        print(f"  ❌ Failed to delete assignment {assignment['id']}")
        
        # Test: Add first assignment
        print("\n📝 Adding first assignment (Developer)...")
        assignment1_data = {
            "entity_type": "userstory",
            "entity_id": userstory_id,
            "user_id": users[0]["id"],
            "assignment_type": "developer"
        }
        
        create1_response = requests.post(f"{base_url}/assignments/", json=assignment1_data, headers=headers)
        if create1_response.status_code not in [200, 201]:
            print(f"❌ Failed to create first assignment: {create1_response.status_code}")
            print(f"Response: {create1_response.text}")
            return
        
        assignment1 = create1_response.json()
        print(f"✅ Created first assignment: {users[0]['full_name']} as Developer")
        
        # Check assignments after first addition
        print("\n🔍 Checking assignments after first addition...")
        check1_response = requests.get(
            f"{base_url}/assignments/", 
            headers=headers,
            params={"entity_type": "userstory", "entity_id": userstory_id}
        )
        
        if check1_response.status_code == 200:
            assignments_after_1 = check1_response.json()
            active_assignments_1 = [a for a in assignments_after_1 if a.get("is_active")]
            print(f"✅ Found {len(active_assignments_1)} active assignments")
            for assignment in active_assignments_1:
                print(f"  - {assignment.get('user_name', 'Unknown')} as {assignment.get('assignment_type', 'Unknown')}")
        else:
            print(f"❌ Failed to check assignments: {check1_response.status_code}")
            return
        
        # Test: Add second assignment
        print("\n📝 Adding second assignment (Tester)...")
        assignment2_data = {
            "entity_type": "userstory",
            "entity_id": userstory_id,
            "user_id": users[1]["id"] if len(users) > 1 else users[0]["id"],
            "assignment_type": "tester"
        }
        
        create2_response = requests.post(f"{base_url}/assignments/", json=assignment2_data, headers=headers)
        if create2_response.status_code not in [200, 201]:
            print(f"❌ Failed to create second assignment: {create2_response.status_code}")
            print(f"Response: {create2_response.text}")
            return
        
        assignment2 = create2_response.json()
        print(f"✅ Created second assignment: {users[1]['full_name'] if len(users) > 1 else users[0]['full_name']} as Tester")
        
        # Check assignments after second addition
        print("\n🔍 Checking assignments after second addition...")
        check2_response = requests.get(
            f"{base_url}/assignments/", 
            headers=headers,
            params={"entity_type": "userstory", "entity_id": userstory_id}
        )
        
        if check2_response.status_code == 200:
            assignments_after_2 = check2_response.json()
            active_assignments_2 = [a for a in assignments_after_2 if a.get("is_active")]
            print(f"✅ Found {len(active_assignments_2)} active assignments")
            
            if len(active_assignments_2) >= 2:
                print("🎉 SUCCESS: Both assignments are persisted!")
                for assignment in active_assignments_2:
                    print(f"  - {assignment.get('user_name', 'Unknown')} as {assignment.get('assignment_type', 'Unknown')}")
            else:
                print("❌ FAILURE: Second assignment overwrote the first one!")
                for assignment in active_assignments_2:
                    print(f"  - {assignment.get('user_name', 'Unknown')} as {assignment.get('assignment_type', 'Unknown')}")
        else:
            print(f"❌ Failed to check assignments: {check2_response.status_code}")
            return
        
        print("\n" + "=" * 50)
        print("🎯 TEST COMPLETE")
        print("Now test in UI:")
        print("1. Go to http://localhost:3007")
        print("2. Navigate to the user story you just tested")
        print("3. Try adding assignments and verify they persist")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_assignment_persistence()
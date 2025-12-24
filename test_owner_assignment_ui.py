#!/usr/bin/env python3
"""
Test Owner Assignment UI Functionality
Tests the owner assignment feature for programs and projects
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8007"
LOGIN_EMAIL = "admin@datalegos.com"
LOGIN_PASSWORD = "password"

def login():
    """Login and get access token"""
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None
    
    token_data = response.json()
    return token_data["access_token"]

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def test_user_role(token):
    """Test if current user is Admin"""
    print("\n🔍 Testing User Role...")
    
    response = requests.get(f"{API_BASE_URL}/api/v1/auth/me", headers=get_headers(token))
    if response.status_code != 200:
        print(f"❌ Failed to get user info: {response.status_code}")
        return False
    
    user_data = response.json()
    print(f"✅ Current user: {user_data.get('full_name')} ({user_data.get('email')})")
    print(f"✅ User role: {user_data.get('role')}")
    
    is_admin = user_data.get('role') == 'Admin'
    print(f"✅ Is Admin: {is_admin}")
    
    return is_admin

def get_eligible_users(token):
    """Get users eligible for ownership (Admin, Owner, Project Manager)"""
    print("\n👥 Getting Eligible Users for Ownership...")
    
    response = requests.get(f"{API_BASE_URL}/api/v1/users", headers=get_headers(token))
    if response.status_code != 200:
        print(f"❌ Failed to get users: {response.status_code}")
        return []
    
    users = response.json()
    eligible_roles = ['Admin', 'Owner', 'Project Manager']
    eligible_users = [u for u in users if u.get('role') in eligible_roles and u.get('full_name')]
    
    print(f"✅ Total users: {len(users)}")
    print(f"✅ Eligible users for ownership: {len(eligible_users)}")
    
    for user in eligible_users:
        print(f"  - {user.get('full_name')} ({user.get('email')}) - {user.get('role')}")
    
    return eligible_users

def test_create_program_with_owner(token, client_id, eligible_users):
    """Test creating a program with owner assignment"""
    print(f"\n🏢 Testing Program Creation with Owner Assignment...")
    
    if not eligible_users:
        print("❌ No eligible users for ownership")
        return None
    
    # Create program
    program_data = {
        "name": f"Test Program with Owner",
        "short_description": "Test program for owner assignment",
        "client_id": client_id,
        "status": "Planning"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/programs", 
                           json=program_data, headers=get_headers(token))
    
    if response.status_code != 201:
        print(f"❌ Failed to create program: {response.status_code} - {response.text}")
        return None
    
    program = response.json()
    program_id = program["id"]
    print(f"✅ Created program: {program['name']} (ID: {program_id})")
    
    # Assign owner
    owner_user = eligible_users[0]  # Use first eligible user
    assignment_data = {
        "entity_type": "program",
        "entity_id": program_id,
        "user_id": owner_user["id"],
        "assignment_type": "owner"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/assignments", 
                           json=assignment_data, headers=get_headers(token))
    
    if response.status_code != 201:
        print(f"❌ Failed to assign owner: {response.status_code} - {response.text}")
        return program_id
    
    assignment = response.json()
    print(f"✅ Assigned owner: {owner_user['full_name']} to program {program['name']}")
    
    return program_id

def test_create_project_with_owner(token, program_id, eligible_users):
    """Test creating a project with owner assignment"""
    print(f"\n📁 Testing Project Creation with Owner Assignment...")
    
    if not eligible_users:
        print("❌ No eligible users for ownership")
        return None
    
    # Create project
    project_data = {
        "name": f"Test Project with Owner",
        "short_description": "Test project for owner assignment",
        "program_id": program_id,
        "status": "Planning"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/projects", 
                           json=project_data, headers=get_headers(token))
    
    if response.status_code != 201:
        print(f"❌ Failed to create project: {response.status_code} - {response.text}")
        return None
    
    project = response.json()
    project_id = project["id"]
    print(f"✅ Created project: {project['name']} (ID: {project_id})")
    
    # Assign owner
    owner_user = eligible_users[0]  # Use first eligible user
    assignment_data = {
        "entity_type": "project",
        "entity_id": project_id,
        "user_id": owner_user["id"],
        "assignment_type": "owner"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/assignments", 
                           json=assignment_data, headers=get_headers(token))
    
    if response.status_code != 201:
        print(f"❌ Failed to assign owner: {response.status_code} - {response.text}")
        return project_id
    
    assignment = response.json()
    print(f"✅ Assigned owner: {owner_user['full_name']} to project {project['name']}")
    
    return project_id

def verify_assignments(token, program_id, project_id):
    """Verify that assignments were created correctly"""
    print(f"\n✅ Verifying Assignments...")
    
    # Check program assignments
    if program_id:
        response = requests.get(f"{API_BASE_URL}/api/v1/assignments?entity_type=program&entity_id={program_id}", 
                              headers=get_headers(token))
        if response.status_code == 200:
            assignments = response.json()
            owner_assignments = [a for a in assignments if a.get('assignment_type') == 'owner']
            print(f"✅ Program has {len(owner_assignments)} owner assignment(s)")
        else:
            print(f"❌ Failed to get program assignments: {response.status_code}")
    
    # Check project assignments
    if project_id:
        response = requests.get(f"{API_BASE_URL}/api/v1/assignments?entity_type=project&entity_id={project_id}", 
                              headers=get_headers(token))
        if response.status_code == 200:
            assignments = response.json()
            owner_assignments = [a for a in assignments if a.get('assignment_type') == 'owner']
            print(f"✅ Project has {len(owner_assignments)} owner assignment(s)")
        else:
            print(f"❌ Failed to get project assignments: {response.status_code}")

def main():
    print("🚀 Testing Owner Assignment UI Functionality")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        sys.exit(1)
    
    print("✅ Login successful")
    
    # Test user role
    is_admin = test_user_role(token)
    if not is_admin:
        print("❌ Current user is not Admin - owner assignment UI should not be visible")
        return
    
    # Get eligible users
    eligible_users = get_eligible_users(token)
    if not eligible_users:
        print("❌ No eligible users found for ownership")
        return
    
    # Get first client for testing
    response = requests.get(f"{API_BASE_URL}/api/v1/clients", headers=get_headers(token))
    if response.status_code != 200:
        print(f"❌ Failed to get clients: {response.status_code}")
        return
    
    clients = response.json()
    print(f"DEBUG: Clients response: {clients}")
    print(f"DEBUG: Clients type: {type(clients)}")
    
    # Handle both list and dict response formats
    if isinstance(clients, dict) and 'clients' in clients:
        clients = clients['clients']
    elif isinstance(clients, dict) and 'items' in clients:
        clients = clients['items']
    
    if not clients or len(clients) == 0:
        print("❌ No clients found")
        return
    
    client_id = clients[0]["id"]
    print(f"✅ Using client: {clients[0]['name']} (ID: {client_id})")
    
    # Test program creation with owner
    program_id = test_create_program_with_owner(token, client_id, eligible_users)
    
    # Test project creation with owner
    project_id = None
    if program_id:
        project_id = test_create_project_with_owner(token, program_id, eligible_users)
    
    # Verify assignments
    verify_assignments(token, program_id, project_id)
    
    print("\n" + "=" * 50)
    print("🎉 Owner Assignment Test Complete!")
    print("\nNext Steps:")
    print("1. Open the UI at http://localhost:3007")
    print("2. Login as admin@datalegos.com / password")
    print("3. Go to Programs page and try creating a new program")
    print("4. Go to Projects page and try creating a new project")
    print("5. Check if the Owner Assignment section appears in the creation forms")

if __name__ == "__main__":
    main()
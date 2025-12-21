#!/usr/bin/env python3
"""
Add admin user to project team to fix assignment issues
"""
import requests
import json

BASE_URL = "http://localhost:8007/api/v1"

def add_admin_to_team():
    """Add admin user to the project team"""
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get teams for project PRJ-000001
    print("1. Getting teams for project PRJ-000001...")
    teams_response = requests.get(f"{BASE_URL}/teams/", headers=headers)
    
    if teams_response.status_code != 200:
        print(f"Failed to get teams: {teams_response.text}")
        return
    
    teams_data = teams_response.json()
    print(f"Teams response: {json.dumps(teams_data, indent=2)}")
    
    # Handle different response formats
    if isinstance(teams_data, list):
        teams = teams_data
    elif isinstance(teams_data, dict) and 'items' in teams_data:
        teams = teams_data['items']
    else:
        teams = []
    
    project_teams = [t for t in teams if t.get('project_id') == 'PRJ-000001']
    
    if not project_teams:
        print("No teams found for project PRJ-000001. Creating one...")
        
        # Create a team for the project
        team_data = {
            "name": "Project Team",
            "description": "Main team for the project",
            "project_id": "PRJ-000001"
        }
        
        create_team_response = requests.post(f"{BASE_URL}/teams/", json=team_data, headers=headers)
        
        if create_team_response.status_code == 201:
            team = create_team_response.json()
            print(f"✅ Created team: {team['name']} (ID: {team['id']})")
            project_teams = [team]
        else:
            print(f"❌ Failed to create team: {create_team_response.text}")
            return
    
    # Add admin user to the first team
    team = project_teams[0]
    print(f"\n2. Adding admin user to team: {team['name']} (ID: {team['id']})")
    
    # Check current team members
    members_response = requests.get(f"{BASE_URL}/teams/{team['id']}/members", headers=headers)
    if members_response.status_code == 200:
        members = members_response.json()
        print(f"Current team members: {len(members)}")
        
        # Check if admin is already a member
        admin_in_team = any(m.get('user_id') == 'USR-001' for m in members)
        if admin_in_team:
            print("✅ Admin user is already a team member")
            return
    
    # Add admin user to team
    member_data = {
        "user_id": "USR-001",
        "role": "Owner"  # Use Owner role for admin user
    }
    
    add_member_response = requests.post(
        f"{BASE_URL}/teams/{team['id']}/members",
        json=member_data,
        headers=headers
    )
    
    if add_member_response.status_code == 201:
        print("✅ Successfully added admin user to team")
        
        # Test assignment again
        print("\n3. Testing assignment after adding admin to team...")
        assignment_data = {
            "entity_type": "userstory",
            "entity_id": "UST-000003",
            "user_id": "USR-001",
            "assignment_type": "owner"
        }
        
        assignment_response = requests.post(
            f"{BASE_URL}/assignments/",
            json=assignment_data,
            headers=headers
        )
        
        print(f"Assignment status: {assignment_response.status_code}")
        if assignment_response.status_code == 201:
            print("✅ Assignment successful!")
            print(f"Response: {json.dumps(assignment_response.json(), indent=2)}")
        else:
            print("❌ Assignment still failed!")
            print(f"Error: {assignment_response.text}")
    else:
        print(f"❌ Failed to add admin to team: {add_member_response.text}")

if __name__ == "__main__":
    add_admin_to_team()
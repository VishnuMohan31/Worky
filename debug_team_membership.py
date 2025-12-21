#!/usr/bin/env python3
"""
Debug team membership issues
"""
import requests
import json

BASE_URL = "http://localhost:8007/api/v1"

def debug_team_membership():
    """Debug team membership for assignment issues"""
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user info
    print("1. Getting current user info...")
    user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if user_response.status_code == 200:
        user = user_response.json()
        print(f"Current user: {user['id']} - {user['full_name']} ({user['email']})")
        print(f"User role: {user.get('role', 'N/A')}")
    
    # Get user story details
    print("\n2. Getting user story details...")
    userstory_response = requests.get(f"{BASE_URL}/hierarchy/userstory/UST-000003", headers=headers)
    if userstory_response.status_code == 200:
        userstory = userstory_response.json()
        print(f"User story: {userstory.get('title', userstory.get('name', 'N/A'))}")
        print(f"Use case ID: {userstory.get('usecase_id', 'N/A')}")
        print(f"Full userstory data: {json.dumps(userstory, indent=2)}")
        
        # Get use case details
        if userstory.get('usecase_id'):
            usecase_response = requests.get(f"{BASE_URL}/hierarchy/usecase/{userstory['usecase_id']}", headers=headers)
            if usecase_response.status_code == 200:
                usecase = usecase_response.json()
                print(f"Use case: {usecase['name']}")
                print(f"Project ID: {usecase.get('project_id', 'N/A')}")
                
                # Get project teams
                if usecase.get('project_id'):
                    print(f"\n3. Getting teams for project {usecase['project_id']}...")
                    teams_response = requests.get(f"{BASE_URL}/teams/", headers=headers)
                    if teams_response.status_code == 200:
                        teams = teams_response.json()
                        project_teams = [t for t in teams if t.get('project_id') == usecase['project_id']]
                        print(f"Found {len(project_teams)} teams for this project")
                        
                        for team in project_teams:
                            print(f"\nTeam: {team['name']} (ID: {team['id']})")
                            
                            # Get team members
                            members_response = requests.get(f"{BASE_URL}/teams/{team['id']}/members", headers=headers)
                            if members_response.status_code == 200:
                                members = members_response.json()
                                print(f"Team members ({len(members)}):")
                                for member in members:
                                    print(f"  - {member.get('user_name', 'N/A')} ({member.get('user_id', 'N/A')}) - {member.get('role', 'N/A')}")
                                    
                                # Check if current user is in team
                                current_user_in_team = any(m.get('user_id') == user['id'] for m in members)
                                print(f"Current user ({user['id']}) in team: {current_user_in_team}")
                    else:
                        print(f"Failed to get teams: {teams_response.text}")
    
    # Test assignment with a team member
    print("\n4. Testing assignment with different users...")
    
    # Get available assignees for userstory
    assignees_response = requests.get(
        f"{BASE_URL}/assignments/available-assignees",
        params={"entity_type": "userstory", "entity_id": "UST-000003"},
        headers=headers
    )
    
    if assignees_response.status_code == 200:
        assignees = assignees_response.json()
        print(f"Available assignees for userstory: {len(assignees)}")
        for assignee in assignees:
            print(f"  - {assignee['full_name']} ({assignee['id']}) - {assignee['role']}")
            
        # Try to assign the first available assignee
        if assignees:
            test_user = assignees[0]
            print(f"\n5. Testing assignment with {test_user['full_name']} ({test_user['id']})...")
            
            # Find a user with compatible role for userstory owner
            compatible_user = None
            for assignee in assignees:
                if assignee['role'] in ['Admin', 'Owner', 'Architect', 'Designer', 'Project Manager']:
                    compatible_user = assignee
                    break
            
            if compatible_user:
                print(f"Found compatible user: {compatible_user['full_name']} ({compatible_user['role']})")
                assignment_data = {
                    "entity_type": "userstory",
                    "entity_id": "UST-000003",
                    "user_id": compatible_user['id'],
                    "assignment_type": "owner"
                }
            else:
                print("No compatible user found, trying with Admin user...")
                assignment_data = {
                    "entity_type": "userstory",
                    "entity_id": "UST-000003",
                    "user_id": "USR-001",  # Admin user
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
                print("❌ Assignment failed!")
                print(f"Error: {assignment_response.text}")
    else:
        print(f"Failed to get available assignees: {assignees_response.text}")

if __name__ == "__main__":
    debug_team_membership()
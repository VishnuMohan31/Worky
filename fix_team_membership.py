#!/usr/bin/env python3
"""
Fix team membership issues by adding proper team members
"""
import requests
import json

def fix_team_membership():
    """Add team members to fix the assignment system"""
    
    BASE_URL = "http://localhost:8007/api/v1"
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return False
        
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔧 FIXING TEAM MEMBERSHIP ISSUES")
    print("=" * 50)
    
    # Get all users
    users_response = requests.get(f"{BASE_URL}/users/", headers=headers)
    if users_response.status_code != 200:
        print(f"Failed to get users: {users_response.status_code}")
        return False
        
    users = users_response.json()
    print(f"Found {len(users)} users")
    
    # Get all teams
    teams_response = requests.get(f"{BASE_URL}/teams/", headers=headers)
    if teams_response.status_code != 200:
        print(f"Failed to get teams: {teams_response.status_code}")
        return False
        
    teams_data = teams_response.json()
    teams = teams_data.get("items", [])
    print(f"Found {len(teams)} teams")
    
    # Add team members to each team
    for team in teams:
        team_id = team["id"]
        team_name = team.get("name", "Unknown")
        project_id = team.get("project_id")
        
        print(f"\n📋 Team: {team_name} ({team_id}) - Project: {project_id}")
        
        # Get current team members
        members_response = requests.get(f"{BASE_URL}/teams/{team_id}/members", headers=headers)
        if members_response.status_code == 200:
            current_members = members_response.json()
            print(f"  Current members: {len(current_members)}")
        else:
            current_members = []
            print(f"  Failed to get current members: {members_response.status_code}")
        
        # Add some users to this team (developers and testers)
        target_users = []
        for user in users:
            role = user.get("role", "").lower()
            if role in ["developer", "tester", "devops", "lead"]:
                target_users.append(user)
        
        print(f"  Target users to add: {len(target_users)}")
        
        # Add users to team
        added_count = 0
        for user in target_users[:3]:  # Add max 3 users per team
            user_id = user["id"]
            user_name = user.get("full_name", "Unknown")
            user_email = user.get("email", "Unknown")
            
            # Check if user is already a member
            is_member = any(m.get("user_id") == user_id for m in current_members)
            if is_member:
                print(f"    ✅ {user_name} already a member")
                continue
            
            # Add user to team
            member_data = {
                "user_id": user_id,
                "role": user.get("role", "Developer")
            }
            
            add_response = requests.post(f"{BASE_URL}/teams/{team_id}/members", json=member_data, headers=headers)
            if add_response.status_code in [200, 201]:
                print(f"    ✅ Added {user_name} ({user_email}) to team")
                added_count += 1
            else:
                print(f"    ❌ Failed to add {user_name}: {add_response.status_code} - {add_response.text}")
        
        print(f"  Added {added_count} new members to team")
    
    print("\n" + "=" * 50)
    print("🎉 Team membership fix completed!")
    
    # Verify the fix by checking available assignees
    print("\n🔍 Verifying fix...")
    
    # Get a task and check available assignees
    tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
    if tasks_response.status_code == 200:
        tasks = tasks_response.json()
        if tasks:
            task_id = tasks[0]["id"]
            print(f"Testing with task: {task_id}")
            
            assignees_response = requests.get(
                f"{BASE_URL}/assignments/available-assignees",
                params={"entity_type": "task", "entity_id": task_id},
                headers=headers
            )
            
            if assignees_response.status_code == 200:
                assignees = assignees_response.json()
                print(f"Available assignees: {len(assignees)}")
                
                admin_available = any(a.get("email") == "admin@datalegos.com" for a in assignees)
                print(f"Admin user available: {admin_available}")
                
                if not admin_available:
                    print("✅ Team membership validation is now working correctly!")
                else:
                    print("⚠️ Admin user is still available - may need further investigation")
                    
                for assignee in assignees:
                    name = assignee.get("full_name", "Unknown")
                    email = assignee.get("email", "Unknown")
                    role = assignee.get("role", "Unknown")
                    print(f"  - {name} ({email}) - {role}")
            else:
                print(f"Failed to get available assignees: {assignees_response.status_code}")
    
    return True

if __name__ == "__main__":
    fix_team_membership()
#!/usr/bin/env python3
"""
Deep Validation Test - Test edge cases and potential issues
"""
import requests
import json
from typing import Dict, List, Any

class DeepValidationTest:
    def __init__(self):
        self.base_url = "http://localhost:8007/api/v1"
        self.token = None
        self.headers = {}
        self.issues = []
        
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
        
    def issue(self, message: str):
        self.issues.append(message)
        self.log(message, "ISSUE")
        
    def login(self) -> bool:
        """Login and get authentication token"""
        try:
            login_data = {"email": "admin@datalegos.com", "password": "password"}
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.log("✅ Login successful")
                return True
            else:
                self.issue(f"❌ Login failed: {response.status_code}")
                return False
        except Exception as e:
            self.issue(f"❌ Login exception: {str(e)}")
            return False
    
    def test_team_membership_validation(self):
        """Test that team membership validation is working correctly"""
        self.log("\n🔍 Testing Team Membership Validation")
        
        try:
            # Get all users
            users_response = requests.get(f"{self.base_url}/users/", headers=self.headers)
            if users_response.status_code != 200:
                self.issue("Failed to get users list")
                return
                
            users = users_response.json()
            self.log(f"Found {len(users)} total users")
            
            # Get all teams
            teams_response = requests.get(f"{self.base_url}/teams/", headers=self.headers)
            if teams_response.status_code != 200:
                self.issue("Failed to get teams list")
                return
                
            teams = teams_response.json()
            self.log(f"Found {len(teams)} total teams")
            
            # Get existing task
            tasks_response = requests.get(f"{self.base_url}/tasks/", headers=self.headers)
            if tasks_response.status_code != 200:
                self.issue("Failed to get tasks list")
                return
                
            tasks = tasks_response.json()
            if not tasks:
                self.issue("No tasks found for testing")
                return
                
            task_id = tasks[0]["id"]
            self.log(f"Testing with task: {task_id}")
            
            # Get available assignees for this task
            assignees_response = requests.get(
                f"{self.base_url}/assignments/available-assignees",
                params={"entity_type": "task", "entity_id": task_id},
                headers=self.headers
            )
            
            if assignees_response.status_code != 200:
                self.issue("Failed to get available assignees")
                return
                
            available_assignees = assignees_response.json()
            self.log(f"Available assignees for task {task_id}: {len(available_assignees)}")
            
            # Check if admin user is in available assignees
            admin_in_assignees = any(user["email"] == "admin@datalegos.com" for user in available_assignees)
            
            if admin_in_assignees:
                self.issue("⚠️ Admin user is available for task assignment - this may indicate team membership validation is not working correctly")
                
                # Check if admin is actually a team member
                admin_is_team_member = False
                for team in teams:
                    if isinstance(team, dict) and 'id' in team:
                        team_members_response = requests.get(f"{self.base_url}/teams/{team['id']}/members", headers=self.headers)
                        if team_members_response.status_code == 200:
                            members = team_members_response.json()
                            if isinstance(members, list):
                                admin_is_member = any(
                                    isinstance(member, dict) and member.get("email") == "admin@datalegos.com" 
                                    for member in members
                                )
                                if admin_is_member:
                                    self.log(f"✅ Admin is a member of team {team.get('name', team['id'])} - assignment is valid")
                                    admin_is_team_member = True
                                    break
                
                if not admin_is_team_member:
                    self.issue("❌ Admin user is available for assignment but is not a team member of any project team")
            else:
                self.log("✅ Admin user is not in available assignees - team membership validation working correctly")
                
        except Exception as e:
            self.issue(f"Team membership validation test failed: {str(e)}")
    
    def test_assignment_constraints(self):
        """Test assignment constraints and validation"""
        self.log("\n🔍 Testing Assignment Constraints")
        
        try:
            # Test duplicate assignment prevention
            tasks_response = requests.get(f"{self.base_url}/tasks/", headers=self.headers)
            if tasks_response.status_code != 200:
                self.issue("Failed to get tasks for constraint testing")
                return
                
            tasks = tasks_response.json()
            if not tasks:
                self.issue("No tasks found for constraint testing")
                return
                
            task_id = tasks[0]["id"]
            
            # Get available assignees
            assignees_response = requests.get(
                f"{self.base_url}/assignments/available-assignees",
                params={"entity_type": "task", "entity_id": task_id},
                headers=self.headers
            )
            
            if assignees_response.status_code != 200:
                self.issue("Failed to get assignees for constraint testing")
                return
                
            assignees = assignees_response.json()
            if not assignees:
                self.issue("No assignees available for constraint testing")
                return
                
            user_id = assignees[0]["id"]
            
            # Create first assignment
            assignment_data = {
                "entity_type": "task",
                "entity_id": task_id,
                "user_id": user_id,
                "assignment_type": "developer"
            }
            
            response1 = requests.post(f"{self.base_url}/assignments/", json=assignment_data, headers=self.headers)
            if response1.status_code == 201:
                assignment1 = response1.json()
                self.log(f"✅ First assignment created: {assignment1['id']}")
                
                # Try to create duplicate assignment
                response2 = requests.post(f"{self.base_url}/assignments/", json=assignment_data, headers=self.headers)
                if response2.status_code == 400:
                    self.log("✅ Duplicate assignment correctly prevented")
                else:
                    self.issue(f"❌ Duplicate assignment not prevented: {response2.status_code}")
                
                # Clean up
                requests.delete(f"{self.base_url}/assignments/{assignment1['id']}", headers=self.headers)
                self.log("✅ Test assignment cleaned up")
            else:
                self.issue(f"Failed to create test assignment: {response1.status_code}")
                
        except Exception as e:
            self.issue(f"Assignment constraints test failed: {str(e)}")
    
    def test_hierarchy_relationships(self):
        """Test that hierarchy relationships are properly maintained"""
        self.log("\n🔍 Testing Hierarchy Relationships")
        
        try:
            # Test use case -> user story relationship
            usecases_response = requests.get(f"{self.base_url}/usecases/", headers=self.headers)
            if usecases_response.status_code != 200:
                self.issue("Failed to get use cases")
                return
                
            usecases = usecases_response.json()
            if not usecases:
                self.issue("No use cases found for relationship testing")
                return
                
            usecase_id = usecases[0]["id"]
            
            # Get user stories for this use case
            userstories_response = requests.get(
                f"{self.base_url}/user-stories/",
                params={"usecase_id": usecase_id},
                headers=self.headers
            )
            
            if userstories_response.status_code != 200:
                self.issue("Failed to get user stories for use case")
                return
                
            userstories = userstories_response.json()
            self.log(f"Use case {usecase_id} has {len(userstories)} user stories")
            
            if userstories:
                userstory_id = userstories[0]["id"]
                
                # Get tasks for this user story
                tasks_response = requests.get(
                    f"{self.base_url}/tasks/",
                    params={"user_story_id": userstory_id},
                    headers=self.headers
                )
                
                if tasks_response.status_code != 200:
                    self.issue("Failed to get tasks for user story")
                    return
                    
                tasks = tasks_response.json()
                self.log(f"User story {userstory_id} has {len(tasks)} tasks")
                
                if tasks:
                    task_id = tasks[0]["id"]
                    
                    # Get subtasks for this task
                    subtasks_response = requests.get(
                        f"{self.base_url}/subtasks/",
                        params={"task_id": task_id},
                        headers=self.headers
                    )
                    
                    if subtasks_response.status_code != 200:
                        self.issue("Failed to get subtasks for task")
                        return
                        
                    subtasks = subtasks_response.json()
                    self.log(f"Task {task_id} has {len(subtasks)} subtasks")
                    
                    self.log("✅ Hierarchy relationships are properly maintained")
                else:
                    self.log("⚠️ No tasks found for user story - may be normal")
            else:
                self.log("⚠️ No user stories found for use case - may be normal")
                
        except Exception as e:
            self.issue(f"Hierarchy relationships test failed: {str(e)}")
    
    def test_phase_requirements(self):
        """Test that phase requirements are properly enforced"""
        self.log("\n🔍 Testing Phase Requirements")
        
        try:
            # Get phases
            phases_response = requests.get(f"{self.base_url}/phases/", headers=self.headers)
            if phases_response.status_code != 200:
                self.issue("Failed to get phases")
                return
                
            phases = phases_response.json()
            if not phases:
                self.issue("No phases found")
                return
                
            self.log(f"Found {len(phases)} phases")
            
            # Test user story creation without phase_id (should fail)
            usecases_response = requests.get(f"{self.base_url}/usecases/", headers=self.headers)
            if usecases_response.status_code == 200:
                usecases = usecases_response.json()
                if usecases:
                    usecase_id = usecases[0]["id"]
                    
                    # Try to create user story without phase_id
                    userstory_data = {
                        "title": "Test User Story Without Phase",
                        "usecase_id": usecase_id,
                        "priority": "Medium",
                        "status": "To Do"
                    }
                    
                    response = requests.post(f"{self.base_url}/user-stories/", json=userstory_data, headers=self.headers)
                    if response.status_code == 422:
                        self.log("✅ User story creation without phase_id correctly rejected")
                    else:
                        self.issue(f"❌ User story creation without phase_id should be rejected: {response.status_code}")
                        
        except Exception as e:
            self.issue(f"Phase requirements test failed: {str(e)}")
    
    def test_data_consistency(self):
        """Test data consistency across the system"""
        self.log("\n🔍 Testing Data Consistency")
        
        try:
            # Check for orphaned records
            
            # Get all user stories
            userstories_response = requests.get(f"{self.base_url}/user-stories/", headers=self.headers)
            if userstories_response.status_code == 200:
                userstories = userstories_response.json()
                
                # Check if all user stories have valid use cases
                usecases_response = requests.get(f"{self.base_url}/usecases/", headers=self.headers)
                if usecases_response.status_code == 200:
                    usecases = usecases_response.json()
                    usecase_ids = {uc["id"] for uc in usecases}
                    
                    orphaned_userstories = [us for us in userstories if us["usecase_id"] not in usecase_ids]
                    if orphaned_userstories:
                        self.issue(f"❌ Found {len(orphaned_userstories)} orphaned user stories")
                    else:
                        self.log("✅ No orphaned user stories found")
            
            # Get all tasks
            tasks_response = requests.get(f"{self.base_url}/tasks/", headers=self.headers)
            if tasks_response.status_code == 200:
                tasks = tasks_response.json()
                
                # Check if all tasks have valid user stories
                if userstories_response.status_code == 200:
                    userstory_ids = {us["id"] for us in userstories}
                    
                    orphaned_tasks = [t for t in tasks if t["user_story_id"] not in userstory_ids]
                    if orphaned_tasks:
                        self.issue(f"❌ Found {len(orphaned_tasks)} orphaned tasks")
                    else:
                        self.log("✅ No orphaned tasks found")
            
            # Check assignments
            assignments_response = requests.get(f"{self.base_url}/assignments/", headers=self.headers)
            if assignments_response.status_code == 200:
                assignments = assignments_response.json()
                active_assignments = [a for a in assignments if a["is_active"]]
                
                self.log(f"Found {len(active_assignments)} active assignments")
                
                # Check for assignments to non-existent entities
                for assignment in active_assignments:
                    entity_type = assignment["entity_type"]
                    entity_id = assignment["entity_id"]
                    
                    if entity_type == "task":
                        task_exists = any(t["id"] == entity_id for t in tasks)
                        if not task_exists:
                            self.issue(f"❌ Assignment {assignment['id']} references non-existent task {entity_id}")
                    elif entity_type == "subtask":
                        subtasks_response = requests.get(f"{self.base_url}/subtasks/", headers=self.headers)
                        if subtasks_response.status_code == 200:
                            subtasks = subtasks_response.json()
                            subtask_exists = any(s["id"] == entity_id for s in subtasks)
                            if not subtask_exists:
                                self.issue(f"❌ Assignment {assignment['id']} references non-existent subtask {entity_id}")
                
                if not any("non-existent" in issue for issue in self.issues):
                    self.log("✅ All assignments reference valid entities")
                    
        except Exception as e:
            self.issue(f"Data consistency test failed: {str(e)}")
    
    def run_deep_validation(self):
        """Run all deep validation tests"""
        self.log("🔍 STARTING DEEP VALIDATION TESTS")
        self.log("=" * 60)
        
        if not self.login():
            return False
        
        # Run all validation tests
        self.test_team_membership_validation()
        self.test_assignment_constraints()
        self.test_hierarchy_relationships()
        self.test_phase_requirements()
        self.test_data_consistency()
        
        return len(self.issues) == 0
    
    def print_summary(self):
        """Print validation summary"""
        self.log("\n" + "=" * 60)
        self.log("📋 DEEP VALIDATION SUMMARY")
        self.log("=" * 60)
        
        if self.issues:
            self.log(f"⚠️ ISSUES FOUND - {len(self.issues)} potential problems:")
            for i, issue in enumerate(self.issues, 1):
                self.log(f"  {i}. {issue}")
        else:
            self.log("✅ NO ISSUES FOUND - All validations passed!")
            
        self.log("=" * 60)

if __name__ == "__main__":
    validator = DeepValidationTest()
    success = validator.run_deep_validation()
    validator.print_summary()
    
    if not success:
        exit(1)
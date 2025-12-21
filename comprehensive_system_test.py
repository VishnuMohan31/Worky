#!/usr/bin/env python3
"""
Comprehensive System Test - Test all hierarchy functionality end-to-end
Tests: Use Cases → User Stories → Tasks → Subtasks → Assignments
"""
import requests
import json
import time
from typing import Dict, List, Any

class ComprehensiveSystemTest:
    def __init__(self):
        self.base_url = "http://localhost:8007/api/v1"
        self.token = None
        self.headers = {}
        self.test_data = {}
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
        
    def error(self, message: str):
        self.errors.append(message)
        self.log(message, "ERROR")
        
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
                self.error(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.error(f"❌ Login exception: {str(e)}")
            return False
    
    def test_hierarchy_chain(self) -> bool:
        """Test the complete hierarchy chain"""
        self.log("\n🔍 TESTING COMPLETE HIERARCHY CHAIN")
        
        # 1. Test Use Case
        if not self.test_usecase_operations():
            return False
            
        # 2. Test User Story
        if not self.test_userstory_operations():
            return False
            
        # 3. Test Task
        if not self.test_task_operations():
            return False
            
        # 4. Test Subtask
        if not self.test_subtask_operations():
            return False
            
        # 5. Test Assignments
        if not self.test_assignment_operations():
            return False
            
        return True
    
    def test_usecase_operations(self) -> bool:
        """Test use case CRUD operations"""
        self.log("\n📋 Testing Use Case Operations")
        
        try:
            # Get existing project for use case creation
            projects_response = requests.get(f"{self.base_url}/projects/", headers=self.headers)
            if projects_response.status_code != 200:
                self.error(f"Failed to get projects: {projects_response.status_code}")
                return False
                
            projects = projects_response.json()
            if not projects:
                self.error("No projects found for use case creation")
                return False
                
            project_id = projects[0]["id"]
            self.test_data["project_id"] = project_id
            self.log(f"Using project: {project_id}")
            
            # Test use case creation
            usecase_data = {
                "name": "Test Use Case - Comprehensive",
                "description": "Test use case for comprehensive testing",
                "project_id": project_id,
                "priority": "High",
                "status": "Planning"
            }
            
            response = requests.post(f"{self.base_url}/usecases/", json=usecase_data, headers=self.headers)
            if response.status_code == 201:
                usecase = response.json()
                self.test_data["usecase_id"] = usecase["id"]
                self.log(f"✅ Use case created: {usecase['id']}")
            else:
                self.error(f"❌ Use case creation failed: {response.status_code} - {response.text}")
                return False
                
            # Test use case retrieval
            response = requests.get(f"{self.base_url}/usecases/{self.test_data['usecase_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Use case retrieval failed: {response.status_code}")
                return False
            else:
                self.log("✅ Use case retrieval successful")
                
            return True
            
        except Exception as e:
            self.error(f"❌ Use case operations exception: {str(e)}")
            return False
    
    def test_userstory_operations(self) -> bool:
        """Test user story CRUD operations"""
        self.log("\n📖 Testing User Story Operations")
        
        try:
            # Get phases for user story creation
            phases_response = requests.get(f"{self.base_url}/phases/", headers=self.headers)
            if phases_response.status_code != 200:
                self.error(f"Failed to get phases: {phases_response.status_code}")
                return False
                
            phases = phases_response.json()
            if not phases:
                self.error("No phases found for user story creation")
                return False
                
            phase_id = phases[0]["id"]
            self.log(f"Using phase: {phase_id}")
            
            # Test user story creation
            userstory_data = {
                "title": "Test User Story - Comprehensive",
                "description": "Test user story for comprehensive testing",
                "usecase_id": self.test_data["usecase_id"],
                "phase_id": phase_id,
                "priority": "High",
                "status": "To Do",
                "story_points": 5
            }
            
            response = requests.post(f"{self.base_url}/user-stories/", json=userstory_data, headers=self.headers)
            if response.status_code == 201:
                userstory = response.json()
                self.test_data["userstory_id"] = userstory["id"]
                self.log(f"✅ User story created: {userstory['id']}")
            else:
                self.error(f"❌ User story creation failed: {response.status_code} - {response.text}")
                return False
                
            # Test user story retrieval
            response = requests.get(f"{self.base_url}/user-stories/{self.test_data['userstory_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ User story retrieval failed: {response.status_code}")
                return False
            else:
                self.log("✅ User story retrieval successful")
                
            return True
            
        except Exception as e:
            self.error(f"❌ User story operations exception: {str(e)}")
            return False
    
    def test_task_operations(self) -> bool:
        """Test task CRUD operations"""
        self.log("\n⚡ Testing Task Operations")
        
        try:
            # Get phases for task creation
            phases_response = requests.get(f"{self.base_url}/phases/", headers=self.headers)
            if phases_response.status_code != 200:
                self.error(f"Failed to get phases: {phases_response.status_code}")
                return False
                
            phases = phases_response.json()
            if not phases:
                self.error("No phases found for task creation")
                return False
                
            phase_id = phases[0]["id"]
            self.log(f"Using phase: {phase_id}")
            
            # Test task creation
            task_data = {
                "title": "Test Task - Comprehensive",
                "short_description": "Test task for comprehensive testing",
                "user_story_id": self.test_data["userstory_id"],
                "phase_id": phase_id,
                "priority": "High",
                "status": "To Do",
                "estimated_hours": 8,
                "story_points": 3
            }
            
            response = requests.post(f"{self.base_url}/tasks/", json=task_data, headers=self.headers)
            if response.status_code == 201:
                task = response.json()
                self.test_data["task_id"] = task["id"]
                self.log(f"✅ Task created: {task['id']}")
            else:
                self.error(f"❌ Task creation failed: {response.status_code} - {response.text}")
                return False
                
            # Test task retrieval
            response = requests.get(f"{self.base_url}/tasks/{self.test_data['task_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Task retrieval failed: {response.status_code}")
                return False
            else:
                self.log("✅ Task retrieval successful")
                
            return True
            
        except Exception as e:
            self.error(f"❌ Task operations exception: {str(e)}")
            return False
    
    def test_subtask_operations(self) -> bool:
        """Test subtask CRUD operations"""
        self.log("\n🔧 Testing Subtask Operations")
        
        try:
            # Test subtask creation
            subtask_data = {
                "title": "Test Subtask - Comprehensive",
                "short_description": "Test subtask for comprehensive testing",
                "task_id": self.test_data["task_id"],
                "status": "To Do",
                "estimated_hours": 2,
                "duration_days": 1
            }
            
            response = requests.post(f"{self.base_url}/subtasks/", json=subtask_data, headers=self.headers)
            if response.status_code == 201:
                subtask = response.json()
                self.test_data["subtask_id"] = subtask["id"]
                self.log(f"✅ Subtask created: {subtask['id']}")
            else:
                self.error(f"❌ Subtask creation failed: {response.status_code} - {response.text}")
                return False
                
            # Test subtask retrieval
            response = requests.get(f"{self.base_url}/subtasks/{self.test_data['subtask_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Subtask retrieval failed: {response.status_code}")
                return False
            else:
                self.log("✅ Subtask retrieval successful")
                
            return True
            
        except Exception as e:
            self.error(f"❌ Subtask operations exception: {str(e)}")
            return False
    
    def test_assignment_operations(self) -> bool:
        """Test assignment operations for tasks and subtasks"""
        self.log("\n👥 Testing Assignment Operations")
        
        try:
            # Get available assignees for task
            response = requests.get(
                f"{self.base_url}/assignments/available-assignees",
                params={"entity_type": "task", "entity_id": self.test_data["task_id"]},
                headers=self.headers
            )
            
            if response.status_code != 200:
                self.error(f"❌ Failed to get available assignees: {response.status_code}")
                return False
                
            assignees = response.json()
            if not assignees:
                self.error("❌ No available assignees found")
                return False
                
            assignee_id = assignees[0]["id"]
            self.log(f"Using assignee: {assignee_id} ({assignees[0]['full_name']})")
            
            # Test task assignment
            assignment_data = {
                "entity_type": "task",
                "entity_id": self.test_data["task_id"],
                "user_id": assignee_id,
                "assignment_type": "developer"
            }
            
            response = requests.post(f"{self.base_url}/assignments/", json=assignment_data, headers=self.headers)
            if response.status_code == 201:
                assignment = response.json()
                self.test_data["task_assignment_id"] = assignment["id"]
                self.log(f"✅ Task assignment created: {assignment['id']}")
            else:
                self.error(f"❌ Task assignment failed: {response.status_code} - {response.text}")
                return False
            
            # Test subtask assignment
            assignment_data = {
                "entity_type": "subtask",
                "entity_id": self.test_data["subtask_id"],
                "user_id": assignee_id,
                "assignment_type": "developer"
            }
            
            response = requests.post(f"{self.base_url}/assignments/", json=assignment_data, headers=self.headers)
            if response.status_code == 201:
                assignment = response.json()
                self.test_data["subtask_assignment_id"] = assignment["id"]
                self.log(f"✅ Subtask assignment created: {assignment['id']}")
            else:
                self.error(f"❌ Subtask assignment failed: {response.status_code} - {response.text}")
                return False
            
            # Test assignment retrieval
            response = requests.get(
                f"{self.base_url}/assignments/",
                params={"entity_type": "task", "entity_id": self.test_data["task_id"]},
                headers=self.headers
            )
            
            if response.status_code != 200:
                self.error(f"❌ Assignment retrieval failed: {response.status_code}")
                return False
            else:
                assignments = response.json()
                active_assignments = [a for a in assignments if a["is_active"]]
                self.log(f"✅ Assignment retrieval successful: {len(active_assignments)} active assignments")
                
            return True
            
        except Exception as e:
            self.error(f"❌ Assignment operations exception: {str(e)}")
            return False
    
    def test_hierarchy_navigation(self) -> bool:
        """Test hierarchy navigation endpoints"""
        self.log("\n🧭 Testing Hierarchy Navigation")
        
        try:
            # Test use case with context
            response = requests.get(f"{self.base_url}/hierarchy/usecase/{self.test_data['usecase_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Use case hierarchy failed: {response.status_code}")
                return False
            else:
                self.log("✅ Use case hierarchy navigation successful")
            
            # Test user story with context
            response = requests.get(f"{self.base_url}/hierarchy/userstory/{self.test_data['userstory_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ User story hierarchy failed: {response.status_code}")
                return False
            else:
                self.log("✅ User story hierarchy navigation successful")
            
            # Test task with context
            response = requests.get(f"{self.base_url}/hierarchy/task/{self.test_data['task_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Task hierarchy failed: {response.status_code}")
                return False
            else:
                self.log("✅ Task hierarchy navigation successful")
            
            # Test subtask with context
            response = requests.get(f"{self.base_url}/hierarchy/subtask/{self.test_data['subtask_id']}", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Subtask hierarchy failed: {response.status_code}")
                return False
            else:
                self.log("✅ Subtask hierarchy navigation successful")
                
            return True
            
        except Exception as e:
            self.error(f"❌ Hierarchy navigation exception: {str(e)}")
            return False
    
    def test_statistics_and_rollups(self) -> bool:
        """Test statistics and rollup calculations"""
        self.log("\n📊 Testing Statistics and Rollups")
        
        try:
            # Test use case statistics
            response = requests.get(f"{self.base_url}/hierarchy/usecase/{self.test_data['usecase_id']}/statistics", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Use case statistics failed: {response.status_code}")
                return False
            else:
                self.log("✅ Use case statistics successful")
            
            # Test user story statistics
            response = requests.get(f"{self.base_url}/hierarchy/userstory/{self.test_data['userstory_id']}/statistics", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ User story statistics failed: {response.status_code}")
                return False
            else:
                self.log("✅ User story statistics successful")
            
            # Test task statistics
            response = requests.get(f"{self.base_url}/hierarchy/task/{self.test_data['task_id']}/statistics", headers=self.headers)
            if response.status_code != 200:
                self.error(f"❌ Task statistics failed: {response.status_code}")
                return False
            else:
                self.log("✅ Task statistics successful")
                
            return True
            
        except Exception as e:
            self.error(f"❌ Statistics testing exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("\n🧹 Cleaning up test data")
        
        try:
            # Delete assignments first
            if "task_assignment_id" in self.test_data:
                requests.delete(f"{self.base_url}/assignments/{self.test_data['task_assignment_id']}", headers=self.headers)
                self.log("✅ Task assignment deleted")
                
            if "subtask_assignment_id" in self.test_data:
                requests.delete(f"{self.base_url}/assignments/{self.test_data['subtask_assignment_id']}", headers=self.headers)
                self.log("✅ Subtask assignment deleted")
            
            # Delete subtask
            if "subtask_id" in self.test_data:
                requests.delete(f"{self.base_url}/subtasks/{self.test_data['subtask_id']}", headers=self.headers)
                self.log("✅ Subtask deleted")
            
            # Delete task
            if "task_id" in self.test_data:
                requests.delete(f"{self.base_url}/tasks/{self.test_data['task_id']}", headers=self.headers)
                self.log("✅ Task deleted")
            
            # Delete user story
            if "userstory_id" in self.test_data:
                requests.delete(f"{self.base_url}/user-stories/{self.test_data['userstory_id']}", headers=self.headers)
                self.log("✅ User story deleted")
            
            # Delete use case
            if "usecase_id" in self.test_data:
                requests.delete(f"{self.base_url}/usecases/{self.test_data['usecase_id']}", headers=self.headers)
                self.log("✅ Use case deleted")
                
        except Exception as e:
            self.log(f"⚠️ Cleanup warning: {str(e)}", "WARN")
    
    def run_comprehensive_test(self):
        """Run the complete comprehensive test suite"""
        self.log("🚀 STARTING COMPREHENSIVE SYSTEM TEST")
        self.log("=" * 60)
        
        # Login
        if not self.login():
            return False
        
        try:
            # Test complete hierarchy chain
            if not self.test_hierarchy_chain():
                return False
            
            # Test hierarchy navigation
            if not self.test_hierarchy_navigation():
                return False
            
            # Test statistics and rollups
            if not self.test_statistics_and_rollups():
                return False
            
            self.log("\n" + "=" * 60)
            self.log("🎉 ALL TESTS PASSED SUCCESSFULLY!")
            self.log("✅ Use Cases → User Stories → Tasks → Subtasks → Assignments")
            self.log("✅ Hierarchy Navigation")
            self.log("✅ Statistics and Rollups")
            self.log("✅ CRUD Operations")
            self.log("✅ Team Assignment System")
            
            return True
            
        except Exception as e:
            self.error(f"❌ Comprehensive test exception: {str(e)}")
            return False
            
        finally:
            # Always cleanup
            self.cleanup_test_data()
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "=" * 60)
        self.log("📋 TEST SUMMARY")
        self.log("=" * 60)
        
        if self.errors:
            self.log(f"❌ FAILED - {len(self.errors)} errors found:")
            for i, error in enumerate(self.errors, 1):
                self.log(f"  {i}. {error}")
        else:
            self.log("✅ SUCCESS - All tests passed!")
            
        self.log("=" * 60)

if __name__ == "__main__":
    tester = ComprehensiveSystemTest()
    success = tester.run_comprehensive_test()
    tester.print_summary()
    
    if not success:
        exit(1)
"""
Integration tests for QA Testing and Bug Management workflows.
Tests the complete end-to-end workflows for test cases, executions, and bugs.
"""
import pytest
import requests
from datetime import datetime
import json

# API Configuration
API_BASE_URL = "http://localhost:8007/api/v1"
LOGIN_EMAIL = "admin@datalegos.com"
LOGIN_PASSWORD = "password"

# Global variables for test data
auth_token = None
test_case_id = None
test_execution_id = None
bug_id = None
project_id = None
user_id = None


def get_auth_token():
    """Get authentication token for API requests."""
    global auth_token
    if auth_token:
        return auth_token
    
    # Login to get token
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )
    
    if response.status_code == 200:
        result = response.json()
        auth_token = result.get("access_token")
        return auth_token
    
    raise Exception(f"Failed to authenticate: {response.status_code} - {response.text}")


def get_headers():
    """Get headers with authentication token."""
    token = get_auth_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def get_test_project():
    """Get a project to use for testing."""
    global project_id
    if project_id:
        return project_id
    
    # Try to get projects from the projects endpoint
    response = requests.get(
        f"{API_BASE_URL}/projects",
        headers=get_headers(),
        params={"skip": 0, "limit": 10}
    )
    
    if response.status_code == 200:
        result = response.json()
        # Handle both list and paginated response formats
        projects = result if isinstance(result, list) else result.get("items", [])
        if projects and len(projects) > 0:
            project_id = projects[0].get("id")
            print(f"Using project: {project_id} - {projects[0].get('name', 'N/A')}")
            return project_id
    
    raise Exception(f"No projects found for testing. Response: {response.status_code} - {response.text}")


def get_test_user():
    """Get a user to use for testing."""
    global user_id
    if user_id:
        return user_id
    
    response = requests.get(
        f"{API_BASE_URL}/users",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        users = response.json()
        if users and len(users) > 0:
            user_id = users[0].get("id")
            return user_id
    
    raise Exception("No users found for testing")


class TestTestCaseWorkflow:
    """Test 16.1: Test case creation and execution workflow"""
    
    def test_01_create_test_case(self):
        """Create a test case via API"""
        global test_case_id
        
        project_id = get_test_project()
        
        test_case_data = {
            "title": f"Integration Test Case - {datetime.now().isoformat()}",
            "description": "This is an integration test case created by automated testing",
            "preconditions": "System is running and user is logged in",
            "test_steps": json.dumps([
                {"step": 1, "action": "Navigate to login page", "expected": "Login page displays"},
                {"step": 2, "action": "Enter credentials", "expected": "Credentials accepted"},
                {"step": 3, "action": "Click login button", "expected": "User is logged in"}
            ]),
            "expected_result": "User successfully logs in and sees dashboard",
            "test_type": "Functional",
            "priority": "P1 (High)",
            "status": "Active",
            "project_id": project_id,
            "tags": json.dumps(["integration", "login", "smoke"])
        }
        
        response = requests.post(
            f"{API_BASE_URL}/test-cases/",
            headers=get_headers(),
            json=test_case_data
        )
        
        print(f"Create test case response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code in [200, 201], f"Failed to create test case: {response.text}"
        
        result = response.json()
        test_case_id = result.get("id")
        
        assert test_case_id is not None, "Test case ID not returned"
        assert result.get("title") == test_case_data["title"]
        assert result.get("test_type") == "Functional"
        assert result.get("priority") == "P1 (High)"
        
        print(f"✓ Test case created successfully: {test_case_id}")
    
    def test_02_execute_test_case(self):
        """Execute test case and record results"""
        global test_execution_id
        
        assert test_case_id is not None, "Test case must be created first"
        
        execution_data = {
            "test_case_id": test_case_id,
            "execution_status": "Failed",
            "actual_result": "Login button did not respond when clicked",
            "execution_notes": "Browser console shows JavaScript error",
            "environment": "Chrome 120, macOS 14",
            "browser": "Chrome 120",
            "os": "macOS 14",
            "device_type": "Desktop"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/test-executions/",
            headers=get_headers(),
            json=execution_data
        )
        
        print(f"Execute test case response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code in [200, 201], f"Failed to execute test case: {response.text}"
        
        result = response.json()
        test_execution_id = result.get("id")
        
        assert test_execution_id is not None, "Test execution ID not returned"
        assert result.get("execution_status") == "Failed"
        assert result.get("test_case_id") == test_case_id
        
        print(f"✓ Test case executed successfully: {test_execution_id}")
    
    def test_03_verify_execution_history(self):
        """Verify execution appears in test case history"""
        assert test_case_id is not None, "Test case must be created first"
        assert test_execution_id is not None, "Test execution must be created first"
        
        response = requests.get(
            f"{API_BASE_URL}/test-cases/{test_case_id}/executions",
            headers=get_headers()
        )
        
        print(f"Get execution history response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code == 200, f"Failed to get execution history: {response.text}"
        
        executions = response.json()
        assert isinstance(executions, list), "Executions should be a list"
        assert len(executions) > 0, "No executions found"
        
        # Find our execution
        found = False
        for execution in executions:
            if execution.get("id") == test_execution_id:
                found = True
                assert execution.get("execution_status") == "Failed"
                break
        
        assert found, f"Test execution {test_execution_id} not found in history"
        
        print(f"✓ Execution history verified: {len(executions)} execution(s) found")
    
    def test_04_create_bug_from_failed_execution(self):
        """Create bug from failed test execution"""
        global bug_id
        
        assert test_execution_id is not None, "Test execution must be created first"
        
        bug_data = {
            "title": f"Bug from failed test - {datetime.now().isoformat()}",
            "description": "Login button not responding - discovered during test execution. Browser console shows JavaScript error when clicking the login button.",
            "severity": "Major",
            "priority": "P1 (High)",
            "bug_type": "Functional"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/test-executions/{test_execution_id}/create-bug",
            headers=get_headers(),
            json=bug_data
        )
        
        print(f"Create bug from execution response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code in [200, 201], f"Failed to create bug: {response.text}"
        
        result = response.json()
        bug_id = result.get("id")
        
        assert bug_id is not None, "Bug ID not returned"
        assert result.get("severity") == "Major"
        assert result.get("status") == "New"
        
        print(f"✓ Bug created from failed execution: {bug_id}")
    
    def test_05_verify_bug_linked_to_test_case(self):
        """Verify bug is linked to test case"""
        assert test_case_id is not None, "Test case must be created first"
        assert bug_id is not None, "Bug must be created first"
        
        # Get test case details to check linked bugs
        response = requests.get(
            f"{API_BASE_URL}/test-cases/{test_case_id}",
            headers=get_headers()
        )
        
        print(f"Get test case details response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code == 200, f"Failed to get test case: {response.text}"
        
        test_case = response.json()
        linked_bugs = test_case.get("linked_bugs", [])
        
        # Check if our bug is in the linked bugs
        bug_ids = [b.get("id") if isinstance(b, dict) else b for b in linked_bugs]
        
        assert bug_id in bug_ids, f"Bug {bug_id} not linked to test case {test_case_id}"
        
        print(f"✓ Bug successfully linked to test case")


def run_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("TASK 16.1: Test Case Creation and Execution Workflow")
    print("="*80 + "\n")
    
    test_suite = TestTestCaseWorkflow()
    
    try:
        print("Test 1: Create test case via API")
        test_suite.test_01_create_test_case()
        print()
        
        print("Test 2: Execute test case and record results")
        test_suite.test_02_execute_test_case()
        print()
        
        print("Test 3: Verify execution appears in history")
        test_suite.test_03_verify_execution_history()
        print()
        
        print("Test 4: Create bug from failed execution")
        test_suite.test_04_create_bug_from_failed_execution()
        print()
        
        print("Test 5: Verify bug is linked to test case")
        test_suite.test_05_verify_bug_linked_to_test_case()
        print()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Task 16.1 Complete")
        print("="*80 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

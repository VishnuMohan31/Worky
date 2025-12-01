#!/usr/bin/env python3
"""
Manual verification script for TODO feature integration.
Tests key functionality without requiring full test setup.
"""
import requests
import json
from datetime import date, timedelta
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_ID = "USR-001"  # Replace with actual test user ID

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(name: str):
    """Print test name."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message: str):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


def make_request(method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> requests.Response:
    """Make API request with authentication."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "X-User-ID": TEST_USER_ID,
        "Content-Type": "application/json"
    }
    
    if method == "GET":
        return requests.get(url, headers=headers, params=params)
    elif method == "POST":
        return requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        return requests.put(url, headers=headers, json=data)
    elif method == "PATCH":
        return requests.patch(url, headers=headers, json=data)
    elif method == "DELETE":
        return requests.delete(url, headers=headers)


def test_todo_lifecycle():
    """Test complete TODO item lifecycle."""
    print_test("TODO Item Lifecycle (Create, Update, Move, Delete)")
    
    # 1. Create TODO
    print_info("Creating TODO item...")
    create_data = {
        "title": "Test TODO Item",
        "description": "This is a test TODO",
        "target_date": str(date.today()),
        "visibility": "private"
    }
    
    response = make_request("POST", "/todos", data=create_data)
    if response.status_code == 201:
        todo = response.json()
        todo_id = todo["id"]
        print_success(f"Created TODO with ID: {todo_id}")
    else:
        print_error(f"Failed to create TODO: {response.status_code} - {response.text}")
        return False
    
    # 2. Update TODO
    print_info("Updating TODO item...")
    update_data = {
        "title": "Updated Test TODO",
        "description": "Updated description"
    }
    
    response = make_request("PUT", f"/todos/{todo_id}", data=update_data)
    if response.status_code == 200:
        print_success("Updated TODO successfully")
    else:
        print_error(f"Failed to update TODO: {response.status_code}")
        return False
    
    # 3. Move TODO to tomorrow
    print_info("Moving TODO to tomorrow...")
    tomorrow = date.today() + timedelta(days=1)
    move_data = {"target_date": str(tomorrow)}
    
    response = make_request("PATCH", f"/todos/{todo_id}/move", data=move_data)
    if response.status_code == 200:
        moved_todo = response.json()
        if moved_todo["target_date"] == str(tomorrow):
            print_success(f"Moved TODO to {tomorrow}")
        else:
            print_error("TODO date not updated correctly")
            return False
    else:
        print_error(f"Failed to move TODO: {response.status_code}")
        return False
    
    # 4. Delete TODO
    print_info("Deleting TODO item...")
    response = make_request("DELETE", f"/todos/{todo_id}")
    if response.status_code == 204:
        print_success("Deleted TODO successfully")
    else:
        print_error(f"Failed to delete TODO: {response.status_code}")
        return False
    
    # 5. Verify deletion
    print_info("Verifying TODO is deleted...")
    response = make_request("GET", f"/todos/{todo_id}")
    if response.status_code == 404:
        print_success("TODO is properly deleted (soft delete)")
    else:
        print_error("TODO still accessible after deletion")
        return False
    
    return True


def test_visibility():
    """Test public/private visibility."""
    print_test("Visibility Controls (Public/Private)")
    
    # Create private TODO
    print_info("Creating private TODO...")
    private_data = {
        "title": "Private TODO",
        "target_date": str(date.today()),
        "visibility": "private"
    }
    
    response = make_request("POST", "/todos", data=private_data)
    if response.status_code == 201:
        private_id = response.json()["id"]
        print_success(f"Created private TODO: {private_id}")
    else:
        print_error(f"Failed to create private TODO: {response.status_code}")
        return False
    
    # Create public TODO
    print_info("Creating public TODO...")
    public_data = {
        "title": "Public TODO",
        "target_date": str(date.today()),
        "visibility": "public"
    }
    
    response = make_request("POST", "/todos", data=public_data)
    if response.status_code == 201:
        public_id = response.json()["id"]
        print_success(f"Created public TODO: {public_id}")
    else:
        print_error(f"Failed to create public TODO: {response.status_code}")
        return False
    
    # Fetch all TODOs
    print_info("Fetching all TODOs...")
    response = make_request("GET", "/todos")
    if response.status_code == 200:
        todos = response.json()["items"]
        print_success(f"Found {len(todos)} TODO items")
        
        # Verify both are present
        ids = [t["id"] for t in todos]
        if private_id in ids and public_id in ids:
            print_success("Both private and public TODOs are accessible to owner")
        else:
            print_error("Not all TODOs are accessible")
            return False
    else:
        print_error(f"Failed to fetch TODOs: {response.status_code}")
        return False
    
    # Clean up
    make_request("DELETE", f"/todos/{private_id}")
    make_request("DELETE", f"/todos/{public_id}")
    
    return True


def test_date_filtering():
    """Test date range filtering."""
    print_test("Date Range Filtering")
    
    # Create TODOs for different dates
    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)
    
    todo_ids = []
    
    for target_date in [yesterday, today, tomorrow]:
        print_info(f"Creating TODO for {target_date}...")
        data = {
            "title": f"TODO for {target_date}",
            "target_date": str(target_date),
            "visibility": "private"
        }
        
        response = make_request("POST", "/todos", data=data)
        if response.status_code == 201:
            todo_ids.append(response.json()["id"])
            print_success(f"Created TODO for {target_date}")
        else:
            print_error(f"Failed to create TODO: {response.status_code}")
            return False
    
    # Fetch all
    print_info("Fetching all TODOs...")
    response = make_request("GET", "/todos")
    if response.status_code == 200:
        all_todos = response.json()["items"]
        print_success(f"Found {len(all_todos)} total TODOs")
    else:
        print_error(f"Failed to fetch TODOs: {response.status_code}")
        return False
    
    # Fetch with date range (today to tomorrow)
    print_info(f"Fetching TODOs from {today} to {tomorrow}...")
    params = {
        "start_date": str(today),
        "end_date": str(tomorrow)
    }
    response = make_request("GET", "/todos", params=params)
    if response.status_code == 200:
        filtered_todos = response.json()["items"]
        print_success(f"Found {len(filtered_todos)} TODOs in date range")
        
        if len(filtered_todos) == 2:
            print_success("Date filtering works correctly")
        else:
            print_error(f"Expected 2 TODOs, got {len(filtered_todos)}")
            return False
    else:
        print_error(f"Failed to fetch filtered TODOs: {response.status_code}")
        return False
    
    # Clean up
    for todo_id in todo_ids:
        make_request("DELETE", f"/todos/{todo_id}")
    
    return True


def test_adhoc_notes():
    """Test ADHOC notes functionality."""
    print_test("ADHOC Notes (Create, Update, Reorder, Delete)")
    
    # Create notes
    note_ids = []
    for i in range(3):
        print_info(f"Creating ADHOC note {i+1}...")
        data = {
            "title": f"Note {i+1}",
            "content": f"Content for note {i+1}",
            "color": "#FFEB3B"
        }
        
        response = make_request("POST", "/adhoc-notes", data=data)
        if response.status_code == 201:
            note_ids.append(response.json()["id"])
            print_success(f"Created note {i+1}")
        else:
            print_error(f"Failed to create note: {response.status_code}")
            return False
    
    # Fetch all notes
    print_info("Fetching all ADHOC notes...")
    response = make_request("GET", "/adhoc-notes")
    if response.status_code == 200:
        notes = response.json()["notes"]
        print_success(f"Found {len(notes)} ADHOC notes")
    else:
        print_error(f"Failed to fetch notes: {response.status_code}")
        return False
    
    # Update a note
    print_info("Updating ADHOC note...")
    update_data = {
        "title": "Updated Note",
        "content": "Updated content",
        "color": "#FF5722"
    }
    response = make_request("PUT", f"/adhoc-notes/{note_ids[0]}", data=update_data)
    if response.status_code == 200:
        print_success("Updated note successfully")
    else:
        print_error(f"Failed to update note: {response.status_code}")
        return False
    
    # Reorder a note
    print_info("Reordering ADHOC note...")
    reorder_data = {"position": 0}
    response = make_request("PATCH", f"/adhoc-notes/{note_ids[2]}/reorder", data=reorder_data)
    if response.status_code == 200:
        print_success("Reordered note successfully")
    else:
        print_error(f"Failed to reorder note: {response.status_code}")
        return False
    
    # Delete a note
    print_info("Deleting ADHOC note...")
    response = make_request("DELETE", f"/adhoc-notes/{note_ids[1]}")
    if response.status_code == 204:
        print_success("Deleted note successfully")
    else:
        print_error(f"Failed to delete note: {response.status_code}")
        return False
    
    # Verify only 2 notes remain
    response = make_request("GET", "/adhoc-notes")
    if response.status_code == 200:
        remaining_notes = response.json()["notes"]
        if len(remaining_notes) == 2:
            print_success("Correct number of notes after deletion")
        else:
            print_error(f"Expected 2 notes, found {len(remaining_notes)}")
            return False
    
    # Clean up
    for note_id in note_ids:
        make_request("DELETE", f"/adhoc-notes/{note_id}")
    
    return True


def main():
    """Run all verification tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TODO Feature Integration Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}API Base URL: {API_BASE_URL}{RESET}")
    print(f"{YELLOW}Test User ID: {TEST_USER_ID}{RESET}")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print_error("API health check failed. Is the API running?")
            return
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {API_BASE_URL}")
        print_info("Please ensure the API is running on http://localhost:8000")
        return
    
    print_success("API is running")
    
    # Run tests
    tests = [
        ("TODO Lifecycle", test_todo_lifecycle),
        ("Visibility Controls", test_visibility),
        ("Date Filtering", test_date_filtering),
        ("ADHOC Notes", test_adhoc_notes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}ALL TESTS PASSED! ✓{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
    else:
        print(f"\n{RED}{'='*60}{RESET}")
        print(f"{RED}SOME TESTS FAILED ✗{RESET}")
        print(f"{RED}{'='*60}{RESET}")


if __name__ == "__main__":
    main()

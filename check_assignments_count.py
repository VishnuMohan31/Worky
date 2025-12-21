#!/usr/bin/env python3
"""
Check assignments count in database
"""
import requests
import json

def check_assignments():
    base_url = "http://localhost:8007/api/v1"
    
    # Login
    login_data = {"email": "admin@datalegos.com", "password": "password"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("Login failed")
        return
        
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all assignments
    response = requests.get(f"{base_url}/assignments/", headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to get assignments: {response.status_code}")
        print(f"Error: {response.text}")
        return
        
    assignments = response.json()
    
    print(f"Total assignments in database: {len(assignments)}")
    
    # Count by status
    active_assignments = [a for a in assignments if a.get("is_active", True)]
    inactive_assignments = [a for a in assignments if not a.get("is_active", True)]
    
    print(f"Active assignments: {len(active_assignments)}")
    print(f"Inactive assignments: {len(inactive_assignments)}")
    
    # Count by entity type
    entity_counts = {}
    for assignment in active_assignments:
        entity_type = assignment.get("entity_type", "unknown")
        entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
    
    print("\nAssignments by entity type:")
    for entity_type, count in entity_counts.items():
        print(f"  {entity_type}: {count}")
    
    # Count by assignment type
    assignment_type_counts = {}
    for assignment in active_assignments:
        assignment_type = assignment.get("assignment_type", "unknown")
        assignment_type_counts[assignment_type] = assignment_type_counts.get(assignment_type, 0) + 1
    
    print("\nAssignments by assignment type:")
    for assignment_type, count in assignment_type_counts.items():
        print(f"  {assignment_type}: {count}")
    
    # Show some sample assignments
    print("\nSample assignments:")
    for i, assignment in enumerate(active_assignments[:5]):
        print(f"  {i+1}. {assignment.get('entity_type')} {assignment.get('entity_id')} -> {assignment.get('user_name')} ({assignment.get('assignment_type')})")

if __name__ == "__main__":
    check_assignments()
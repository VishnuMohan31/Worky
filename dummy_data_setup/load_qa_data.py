"""
Load QA dummy data using API endpoints
This script uses the real API endpoints to create test cases, executions, bugs, and comments
"""
import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
from config import EXCEL_DIR
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8007/api/v1')
API_USER_EMAIL = os.getenv('API_USER_EMAIL', 'admin@datalegos.com')
API_USER_PASSWORD = os.getenv('API_USER_PASSWORD', 'password')

# Global variables
access_token = None
session = requests.Session()

def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)
    print()

def print_progress(text):
    """Print progress message"""
    print(f"  {text}")

def authenticate():
    """Authenticate with the API and get access token"""
    global access_token
    
    print_progress("Authenticating with API...")
    
    try:
        response = session.post(
            f"{API_BASE_URL}/auth/login",
            data={
                'username': API_USER_EMAIL,
                'password': API_USER_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            session.headers.update({'Authorization': f'Bearer {access_token}'})
            print_progress(f"✓ Authenticated as {API_USER_EMAIL}")
            return True
        else:
            print_progress(f"✗ Authentication failed: {response.status_code}")
            print_progress(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_progress(f"✗ Authentication error: {e}")
        return False

def load_excel_file(filename):
    """Load data from Excel file"""
    filepath = os.path.join(EXCEL_DIR, filename)
    try:
        df = pd.read_excel(filepath)
        # Replace NaN with None
        df = df.where(pd.notnull(df), None)
        return df
    except FileNotFoundError:
        print_progress(f"Warning: File not found: {filepath}")
        return None
    except Exception as e:
        print_progress(f"Error reading {filename}: {e}")
        return None

def create_test_run(test_run_data, created_test_runs):
    """Create a test run via API"""
    try:
        # Prepare payload
        payload = {
            'name': test_run_data['Name'],
            'purpose': test_run_data['Purpose'],
            'short_description': test_run_data['Short Description'],
            'long_description': test_run_data['Long Description'],
            'component_attached_to': test_run_data['Component Attached To'],
            'run_type': test_run_data['Run Type'],
            'status': test_run_data['Status'],
            'start_date': test_run_data['Start Date'],
            'created_by': test_run_data['Created By']
        }
        
        if test_run_data['End Date']:
            payload['end_date'] = test_run_data['End Date']
        
        # Add hierarchy association
        if test_run_data['Project ID']:
            payload['project_id'] = test_run_data['Project ID']
        elif test_run_data['Use Case ID']:
            payload['usecase_id'] = test_run_data['Use Case ID']
        elif test_run_data['User Story ID']:
            payload['user_story_id'] = test_run_data['User Story ID']
        elif test_run_data['Task ID']:
            payload['task_id'] = test_run_data['Task ID']
        elif test_run_data['Subtask ID']:
            payload['subtask_id'] = test_run_data['Subtask ID']
        
        response = session.post(
            f"{API_BASE_URL}/test-runs/",
            json=payload
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            created_test_runs[test_run_data['ID']] = result.get('id')
            return result
        else:
            print_progress(f"  ✗ Failed to create test run: {response.status_code}")
            print_progress(f"    {response.text[:200]}")
            return None
    except Exception as e:
        print_progress(f"  ✗ Error creating test run: {e}")
        return None

def create_test_case(test_case_data, created_test_runs):
    """Create a test case via API"""
    try:
        # Map test run ID
        test_run_id = None
        if test_case_data['Test Run ID'] and test_case_data['Test Run ID'] in created_test_runs:
            test_run_id = created_test_runs[test_case_data['Test Run ID']]
        
        # Prepare payload
        payload = {
            'test_run_id': test_run_id,
            'test_case_name': test_case_data['Test Case Name'],
            'test_case_description': test_case_data['Test Case Description'],
            'test_case_steps': test_case_data['Test Case Steps'],
            'expected_result': test_case_data['Expected Result'],
            'component_attached_to': test_case_data['Component Attached To'],
            'priority': test_case_data['Priority'],
            'status': test_case_data['Status'],
            'created_by': test_case_data['Created By']
        }
        
        # Add optional fields
        if test_case_data['Actual Result']:
            payload['actual_result'] = test_case_data['Actual Result']
        if test_case_data['Inference']:
            payload['inference'] = test_case_data['Inference']
        if test_case_data['Remarks']:
            payload['remarks'] = test_case_data['Remarks']
        if test_case_data['Executed By']:
            payload['executed_by'] = test_case_data['Executed By']
        if test_case_data['Executed At']:
            payload['executed_at'] = test_case_data['Executed At']
        
        response = session.post(
            f"{API_BASE_URL}/test-cases/",
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print_progress(f"  ✗ Failed to create test case: {response.status_code}")
            print_progress(f"    {response.text[:200]}")
            return None
    except Exception as e:
        print_progress(f"  ✗ Error creating test case: {e}")
        return None

def create_bug(bug_data, created_test_runs, created_test_cases):
    """Create a bug via API"""
    try:
        # Map test run and test case IDs
        test_run_id = None
        test_case_id = None
        if bug_data['Test Run ID'] and bug_data['Test Run ID'] in created_test_runs:
            test_run_id = created_test_runs[bug_data['Test Run ID']]
        if bug_data['Test Case ID'] and bug_data['Test Case ID'] in created_test_cases:
            test_case_id = created_test_cases[bug_data['Test Case ID']]
        
        payload = {
            'title': bug_data['Title'],
            'short_description': bug_data['Short Description'],
            'long_description': bug_data['Long Description'],
            'category': bug_data['Category'],
            'severity': bug_data['Severity'],
            'priority': bug_data['Priority'],
            'status': bug_data['Status'],
            'reporter_id': bug_data['Reporter ID'],
            'reproduction_steps': bug_data['Reproduction Steps'],
            'expected_result': bug_data['Expected Result'],
            'actual_result': bug_data['Actual Result'],
            'component_attached_to': bug_data['Component Attached To'],
            'environment': bug_data['Environment']
        }
        
        # Add test run and test case links
        if test_run_id:
            payload['test_run_id'] = test_run_id
        if test_case_id:
            payload['test_case_id'] = test_case_id
        
        # Add hierarchy association (for direct bugs)
        if bug_data['Project ID']:
            payload['project_id'] = bug_data['Project ID']
        if bug_data['Use Case ID']:
            payload['usecase_id'] = bug_data['Use Case ID']
        if bug_data['User Story ID']:
            payload['user_story_id'] = bug_data['User Story ID']
        if bug_data['Task ID']:
            payload['task_id'] = bug_data['Task ID']
        if bug_data['Subtask ID']:
            payload['subtask_id'] = bug_data['Subtask ID']
        
        # Add optional fields
        if bug_data['Assignee ID']:
            payload['assignee_id'] = bug_data['Assignee ID']
        if bug_data['QA Owner ID']:
            payload['qa_owner_id'] = bug_data['QA Owner ID']
        if bug_data['Linked Task ID']:
            payload['linked_task_id'] = bug_data['Linked Task ID']
        if bug_data['Linked Commit']:
            payload['linked_commit'] = bug_data['Linked Commit']
        if bug_data['Linked PR']:
            payload['linked_pr'] = bug_data['Linked PR']
        if bug_data['Reopen Count']:
            payload['reopen_count'] = int(bug_data['Reopen Count'])
        if bug_data['Resolution Notes']:
            payload['resolution_notes'] = bug_data['Resolution Notes']
        if bug_data['Created At']:
            payload['created_at'] = bug_data['Created At']
        if bug_data['Closed At']:
            payload['closed_at'] = bug_data['Closed At']
        
        response = session.post(
            f"{API_BASE_URL}/bugs/",
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print_progress(f"  ✗ Failed to create bug: {response.status_code}")
            print_progress(f"    {response.text[:200]}")
            return None
    except Exception as e:
        print_progress(f"  ✗ Error creating bug: {e}")
        return None

def create_comment(comment_data):
    """Create a comment via API"""
    try:
        payload = {
            'comment_text': comment_data['Comment Text'],
            'author_id': comment_data['Author ID'],
            'mentioned_users': comment_data['Mentioned Users'],
            'attachments': comment_data['Attachments']
        }
        
        # Determine endpoint based on entity type
        if comment_data['Bug ID']:
            endpoint = f"{API_BASE_URL}/bugs/{comment_data['Bug ID']}/comments"
        elif comment_data['Test Case ID']:
            endpoint = f"{API_BASE_URL}/test-cases/{comment_data['Test Case ID']}/comments"
        else:
            print_progress("  ✗ Comment has no entity association")
            return None
        
        response = session.post(endpoint, json=payload)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print_progress(f"  ✗ Failed to create comment: {response.status_code}")
            return None
    except Exception as e:
        print_progress(f"  ✗ Error creating comment: {e}")
        return None

def update_bug_status(bug_id, status_data):
    """Update bug status via API"""
    try:
        payload = {
            'status': status_data['To Status']
        }
        
        if status_data['Resolution Type']:
            payload['resolution_type'] = status_data['Resolution Type']
        if status_data['Notes']:
            payload['notes'] = status_data['Notes']
        
        response = session.post(
            f"{API_BASE_URL}/bugs/{bug_id}/status",
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def assign_bug(bug_id, assignee_id):
    """Assign bug to user via API"""
    try:
        response = session.post(
            f"{API_BASE_URL}/bugs/{bug_id}/assign",
            json={'assignee_id': assignee_id}
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def load_all_data():
    """Load all QA data via API"""
    print_header("QA Data Loader - Using API Endpoints")
    
    # Authenticate
    if not authenticate():
        print_progress("✗ Authentication failed. Cannot proceed.")
        sys.exit(1)
    
    print()
    
    # Track created entities
    created_test_runs = {}
    created_test_cases = {}
    created_bugs = {}
    stats = {
        'test_runs': 0,
        'test_cases': 0,
        'bugs': 0,
        'comments': 0,
        'status_updates': 0,
        'assignments': 0
    }
    
    # Load test runs
    print_header("Loading Test Runs")
    df_test_runs = load_excel_file('test_runs.xlsx')
    if df_test_runs is not None:
        print_progress(f"Found {len(df_test_runs)} test runs to create")
        for idx, row in df_test_runs.iterrows():
            result = create_test_run(row, created_test_runs)
            if result:
                stats['test_runs'] += 1
                if (idx + 1) % 5 == 0:
                    print_progress(f"  Created {idx + 1}/{len(df_test_runs)} test runs...")
        print_progress(f"✓ Created {stats['test_runs']} test runs")
    
    # Load test cases
    print_header("Loading Test Cases")
    df_test_cases = load_excel_file('test_cases.xlsx')
    if df_test_cases is not None:
        print_progress(f"Found {len(df_test_cases)} test cases to create")
        for idx, row in df_test_cases.iterrows():
            result = create_test_case(row, created_test_runs)
            if result:
                created_test_cases[row['ID']] = result.get('id')
                stats['test_cases'] += 1
                if (idx + 1) % 10 == 0:
                    print_progress(f"  Created {idx + 1}/{len(df_test_cases)} test cases...")
        print_progress(f"✓ Created {stats['test_cases']} test cases")
    
    # Load bugs
    print_header("Loading Bugs")
    df_bugs = load_excel_file('bugs_extended.xlsx')
    if df_bugs is not None:
        print_progress(f"Found {len(df_bugs)} bugs to create")
        for idx, row in df_bugs.iterrows():
            result = create_bug(row, created_test_runs, created_test_cases)
            if result:
                created_bugs[row['ID']] = result.get('id')
                stats['bugs'] += 1
                if (idx + 1) % 10 == 0:
                    print_progress(f"  Created {idx + 1}/{len(df_bugs)} bugs...")
        print_progress(f"✓ Created {stats['bugs']} bugs")
    
    # Load comments
    print_header("Loading Comments")
    df_comments = load_excel_file('comments.xlsx')
    if df_comments is not None:
        print_progress(f"Found {len(df_comments)} comments to create")
        for idx, row in df_comments.iterrows():
            # Map old IDs to new IDs
            if row['Bug ID'] and row['Bug ID'] in created_bugs:
                row['Bug ID'] = created_bugs[row['Bug ID']]
            elif row['Test Case ID'] and row['Test Case ID'] in created_test_cases:
                row['Test Case ID'] = created_test_cases[row['Test Case ID']]
            else:
                continue  # Skip if entity not found
            
            result = create_comment(row)
            if result:
                stats['comments'] += 1
                if (idx + 1) % 20 == 0:
                    print_progress(f"  Created {idx + 1}/{len(df_comments)} comments...")
        print_progress(f"✓ Created {stats['comments']} comments")
    
    # Load bug status history
    print_header("Loading Bug Status History")
    df_history = load_excel_file('bug_status_history.xlsx')
    if df_history is not None:
        print_progress(f"Found {len(df_history)} status updates to apply")
        for idx, row in df_history.iterrows():
            # Map old bug ID to new ID
            if row['Bug ID'] in created_bugs:
                bug_id = created_bugs[row['Bug ID']]
                result = update_bug_status(bug_id, row)
                if result:
                    stats['status_updates'] += 1
                    if (idx + 1) % 20 == 0:
                        print_progress(f"  Applied {idx + 1}/{len(df_history)} status updates...")
        print_progress(f"✓ Applied {stats['status_updates']} status updates")
    
    # Load bug assignments
    print_header("Loading Bug Assignments")
    df_assignments = load_excel_file('bug_assignments.xlsx')
    if df_assignments is not None:
        print_progress(f"Found {len(df_assignments)} assignments to apply")
        for idx, row in df_assignments.iterrows():
            # Map old bug ID to new ID
            if row['Bug ID'] in created_bugs:
                bug_id = created_bugs[row['Bug ID']]
                result = assign_bug(bug_id, row['Assigned To'])
                if result:
                    stats['assignments'] += 1
                    if (idx + 1) % 10 == 0:
                        print_progress(f"  Applied {idx + 1}/{len(df_assignments)} assignments...")
        print_progress(f"✓ Applied {stats['assignments']} assignments")
    
    # Print summary
    print_header("Data Loading Complete!")
    print("Summary:")
    print(f"  ✓ Test Runs: {stats['test_runs']}")
    print(f"  ✓ Test Cases: {stats['test_cases']}")
    print(f"  ✓ Bugs: {stats['bugs']}")
    print(f"  ✓ Comments: {stats['comments']}")
    print(f"  ✓ Status Updates: {stats['status_updates']}")
    print(f"  ✓ Assignments: {stats['assignments']}")
    print()
    print("QA data has been loaded successfully via API!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        load_all_data()
    except KeyboardInterrupt:
        print()
        print("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"Error: {e}")
        sys.exit(1)

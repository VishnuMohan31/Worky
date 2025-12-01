"""
Create Excel templates for QA data with sample rows and instructions
"""
import os
import pandas as pd
from config import EXCEL_DIR

def create_test_runs_template():
    """Create test_runs.xlsx template"""
    # Sample data with instructions
    data = [
        {
            'ID': 'TR-001',
            'Project ID': 'PRJ-001',
            'Use Case ID': '',
            'User Story ID': '',
            'Task ID': '',
            'Subtask ID': '',
            'Name': 'Login Module Test Run',
            'Purpose': 'Verify all login functionality',
            'Short Description': 'Comprehensive testing of login features',
            'Long Description': 'This test run covers all aspects of the login module including authentication, password reset, and session management.',
            'Component Attached To': 'Authentication Module',
            'Run Type': 'Misc',
            'Status': 'In Progress',
            'Start Date': '2025-01-15',
            'End Date': '2025-01-20',
            'Created By': 'USR-001'
        },
        {
            'ID': 'TR-002',
            'Project ID': '',
            'Use Case ID': 'UC-001',
            'User Story ID': '',
            'Task ID': '',
            'Subtask ID': '',
            'Name': 'User Management Regression',
            'Purpose': 'Regression testing after recent changes',
            'Short Description': 'Verify no regressions in user management',
            'Long Description': 'Full regression test suite for user management features after the latest deployment.',
            'Component Attached To': 'User Management',
            'Run Type': 'One-Timer',
            'Status': 'Completed',
            'Start Date': '2025-01-10',
            'End Date': '2025-01-12',
            'Created By': 'USR-001'
        },
        {
            'ID': '# INSTRUCTIONS',
            'Project ID': 'Only ONE hierarchy field should be filled',
            'Use Case ID': 'Leave others empty',
            'User Story ID': 'Valid hierarchy: Project, UseCase, UserStory, Task, Subtask',
            'Task ID': '',
            'Subtask ID': '',
            'Name': 'Test run name (required)',
            'Purpose': 'Purpose of this test run',
            'Short Description': 'Brief description (max 500 chars)',
            'Long Description': 'Detailed description with context',
            'Component Attached To': 'Component/module being tested',
            'Run Type': 'Misc or One-Timer',
            'Status': 'In Progress, Completed, or Aborted',
            'Start Date': 'YYYY-MM-DD format',
            'End Date': 'YYYY-MM-DD format',
            'Created By': 'User ID (e.g., USR-001)'
        }
    ]
    
    df = pd.DataFrame(data)
    filepath = os.path.join(EXCEL_DIR, 'test_runs.xlsx')
    df.to_excel(filepath, index=False, sheet_name='Test Runs')
    print(f"✓ Created test_runs.xlsx template")
    return filepath

def update_test_cases_template():
    """Update test_cases.xlsx template with new fields"""
    # Read existing template
    filepath = os.path.join(EXCEL_DIR, 'test_cases.xlsx')
    
    # Create updated template with test_run_id
    data = [
        {
            'ID': 'TC-001',
            'Test Run ID': 'TR-001',
            'Test Case Name': 'Verify login with valid credentials',
            'Test Case Description': 'Test that users can log in with correct email and password',
            'Test Case Steps': '["1. Navigate to login page", "2. Enter valid email", "3. Enter valid password", "4. Click Login button", "5. Verify dashboard loads"]',
            'Expected Result': 'User successfully logs in and dashboard is displayed',
            'Actual Result': '',
            'Inference': '',
            'Component Attached To': 'Login Screen',
            'Remarks': '',
            'Priority': 'P0',
            'Status': 'Not Executed',
            'Executed By': '',
            'Executed At': '',
            'Created By': 'USR-001'
        },
        {
            'ID': 'TC-002',
            'Test Run ID': 'TR-001',
            'Test Case Name': 'Verify login with invalid password',
            'Test Case Description': 'Test that login fails with incorrect password',
            'Test Case Steps': '["1. Navigate to login page", "2. Enter valid email", "3. Enter invalid password", "4. Click Login button", "5. Verify error message"]',
            'Expected Result': 'Error message displayed: Invalid credentials',
            'Actual Result': '',
            'Inference': '',
            'Component Attached To': 'Login Screen',
            'Remarks': '',
            'Priority': 'P1',
            'Status': 'Not Executed',
            'Executed By': '',
            'Executed At': '',
            'Created By': 'USR-001'
        },
        {
            'ID': '# INSTRUCTIONS',
            'Test Run ID': 'Test Run ID (e.g., TR-001) - required',
            'Test Case Name': 'Test case name (required)',
            'Test Case Description': 'Detailed description of what is being tested',
            'Test Case Steps': 'JSON array of numbered steps',
            'Expected Result': 'What should happen (required)',
            'Actual Result': 'What actually happened (filled during execution)',
            'Inference': 'Analysis/conclusion after execution',
            'Component Attached To': 'Component/module being tested',
            'Remarks': 'Additional notes or observations',
            'Priority': 'P0, P1, P2, or P3',
            'Status': 'Not Executed, Passed, Failed, Blocked, Skipped',
            'Executed By': 'User ID who executed (e.g., USR-001)',
            'Executed At': 'YYYY-MM-DD HH:MM:SS format',
            'Created By': 'User ID (e.g., USR-001)'
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False, sheet_name='Test Cases')
    print(f"✓ Updated test_cases.xlsx template")
    return filepath

def update_bugs_extended_template():
    """Update bugs_extended.xlsx template with all new QA fields"""
    filepath = os.path.join(EXCEL_DIR, 'bugs_extended.xlsx')
    
    data = [
        {
            'ID': 'BUG-001',
            'Test Run ID': 'TR-001',
            'Test Case ID': 'TC-001',
            'Project ID': '',
            'Use Case ID': '',
            'User Story ID': '',
            'Task ID': '',
            'Subtask ID': '',
            'Title': 'Login fails with special characters in password',
            'Short Description': 'Password validation issue',
            'Long Description': 'When password contains special characters like @ or #, login fails even with correct credentials.',
            'Category': 'Backend',
            'Severity': 'High',
            'Priority': 'P1',
            'Status': 'New',
            'Reporter ID': 'USR-001',
            'Assignee ID': '',
            'QA Owner ID': 'USR-001',
            'Reproduction Steps': '1. Go to login page\n2. Enter email: test@example.com\n3. Enter password with @ symbol\n4. Click Login\n5. Observe error',
            'Expected Result': 'User should be able to log in successfully',
            'Actual Result': 'Login fails with error: Invalid password format',
            'Component Attached To': 'Authentication Service',
            'Environment': 'Production',
            'Linked Task ID': 'TSK-001',
            'Linked Commit': '',
            'Linked PR': '',
            'Reopen Count': 0,
            'Resolution Notes': '',
            'Created At': '2025-01-15 10:30:00',
            'Closed At': ''
        },
        {
            'ID': 'BUG-002',
            'Test Run ID': '',
            'Test Case ID': '',
            'Project ID': 'PRJ-001',
            'Use Case ID': '',
            'User Story ID': '',
            'Task ID': '',
            'Subtask ID': '',
            'Title': 'Dashboard loads slowly on mobile devices',
            'Short Description': 'Performance issue on mobile',
            'Long Description': 'Dashboard takes more than 5 seconds to load on mobile devices, impacting user experience.',
            'Category': 'Performance',
            'Severity': 'Medium',
            'Priority': 'P2',
            'Status': 'Open',
            'Reporter ID': 'USR-001',
            'Assignee ID': 'USR-001',
            'QA Owner ID': 'USR-001',
            'Reproduction Steps': '1. Open app on mobile device\n2. Log in\n3. Navigate to dashboard\n4. Measure load time',
            'Expected Result': 'Dashboard should load within 2 seconds',
            'Actual Result': 'Dashboard takes 5-7 seconds to load',
            'Component Attached To': 'Dashboard',
            'Environment': 'Mobile - iOS',
            'Linked Task ID': '',
            'Linked Commit': '',
            'Linked PR': '',
            'Reopen Count': 0,
            'Resolution Notes': '',
            'Created At': '2025-01-14 14:20:00',
            'Closed At': ''
        },
        {
            'ID': '# INSTRUCTIONS',
            'Test Run ID': 'Link to test run if bug from test case',
            'Test Case ID': 'Link to test case if bug from test failure',
            'Project ID': 'For direct bugs: fill ONE hierarchy field',
            'Use Case ID': 'Leave others empty',
            'User Story ID': 'Valid: Project, UseCase, UserStory, Task, Subtask',
            'Task ID': '',
            'Subtask ID': '',
            'Title': 'Bug title (required)',
            'Short Description': 'Brief description',
            'Long Description': 'Detailed description with impact',
            'Category': 'UI, Backend, Database, Integration, Performance, Security, Environment',
            'Severity': 'Critical, High, Medium, Low',
            'Priority': 'P1, P2, P3, P4',
            'Status': 'New, Open, In Progress, Fixed, In Review, Ready for QA, Verified, Closed, Reopened',
            'Reporter ID': 'User ID who reported (e.g., USR-001)',
            'Assignee ID': 'User ID assigned to fix',
            'QA Owner ID': 'User ID of QA owner',
            'Reproduction Steps': 'Step-by-step instructions to reproduce',
            'Expected Result': 'What should happen',
            'Actual Result': 'What actually happens',
            'Component Attached To': 'Component/module affected',
            'Environment': 'Where bug was found (e.g., Production, Staging)',
            'Linked Task ID': 'Related task ID',
            'Linked Commit': 'Git commit hash',
            'Linked PR': 'Pull request URL',
            'Reopen Count': 'Number of times reopened (integer)',
            'Resolution Notes': 'Notes when bug is resolved',
            'Created At': 'YYYY-MM-DD HH:MM:SS format',
            'Closed At': 'YYYY-MM-DD HH:MM:SS format (when closed)'
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False, sheet_name='Bugs Extended')
    print(f"✓ Updated bugs_extended.xlsx template")
    return filepath

def main():
    """Create all QA Excel templates"""
    print("Creating QA Excel templates...")
    print()
    
    # Ensure excel_templates directory exists
    os.makedirs(EXCEL_DIR, exist_ok=True)
    
    # Create/update templates
    test_runs_file = create_test_runs_template()
    test_cases_file = update_test_cases_template()
    bugs_file = update_bugs_extended_template()
    
    print()
    print("=" * 60)
    print("QA Excel templates created successfully!")
    print()
    print("Files created/updated:")
    print(f"  - {test_runs_file}")
    print(f"  - {test_cases_file}")
    print(f"  - {bugs_file}")
    print()
    print("Each template includes:")
    print("  - Sample data rows showing the format")
    print("  - Instructions row explaining each field")
    print()
    print("Next steps:")
    print("  1. Review the templates")
    print("  2. Fill in your data following the examples")
    print("  3. Run: python3 create_qa_data.py (to generate dummy data)")
    print("  4. Run: python3 load_qa_data.py (to load data into database)")
    print("=" * 60)

if __name__ == '__main__':
    main()

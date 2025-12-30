"""
Generate realistic QA dummy data (test runs, test cases, bugs)
This script generates data programmatically with realistic distributions
Following the QA Testing and Bug Management spec requirements
"""
import os
import random
import json
from datetime import datetime, timedelta
import pandas as pd
from config import EXCEL_DIR

# Seed for reproducibility
random.seed(42)

# Reference data from existing templates
PROJECTS = ['PRJ-001']
USECASES = ['UC-001']
USER_STORIES = ['US-001']
TASKS = ['TSK-001']
SUBTASKS = ['ST-001']
USERS = ['USR-001']

# Test run data
TEST_RUN_TYPES = ['Misc', 'One-Timer']
TEST_RUN_STATUSES = ['In Progress', 'Completed', 'Aborted']

# Test case data
TEST_TYPES = ['Functional', 'Integration', 'Regression', 'Smoke', 'Sanity', 'Performance', 'Security', 'Usability', 'Acceptance']
PRIORITIES = ['P0', 'P1', 'P2', 'P3']
TEST_CASE_STATUSES = ['Not Executed', 'Passed', 'Failed', 'Blocked', 'Skipped']

# Bug data
BUG_TYPES = ['Functional', 'Performance', 'Security', 'UI/UX', 'Data', 'Integration', 'Configuration']
BUG_SEVERITIES = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']
BUG_PRIORITIES = ['P0', 'P1', 'P2', 'P3', 'P4']
BUG_STATUSES = ['New', 'Open', 'In Progress', 'Fixed', 'Ready for Testing', 'Retest', 'Verified', 'Closed', 'Reopened', 'Deferred', 'Rejected']
RESOLUTION_TYPES = ['Fixed', 'Duplicate', 'Cannot Reproduce', "Won't Fix", 'By Design', 'Deferred']

# Execution data
EXECUTION_STATUSES = ['Passed', 'Failed', 'Blocked', 'Skipped', 'Not Applicable']
BROWSERS = ['Chrome 120', 'Firefox 121', 'Safari 17', 'Edge 120']
OPERATING_SYSTEMS = ['Windows 11', 'macOS 14', 'Ubuntu 22.04', 'iOS 17', 'Android 14']
DEVICE_TYPES = ['Desktop', 'Laptop', 'Mobile', 'Tablet']

# Test case templates
TEST_CASE_TEMPLATES = [
    {
        'title': 'Verify {} functionality with valid input',
        'description': 'Test that {} works correctly with valid data',
        'preconditions': 'System is running and {} is accessible',
        'test_type': 'Functional',
        'priority': 'P1'
    },
    {
        'title': 'Verify {} handles invalid input correctly',
        'description': 'Test that {} properly validates and rejects invalid data',
        'preconditions': 'System is running',
        'test_type': 'Functional',
        'priority': 'P2'
    },
    {
        'title': 'Verify {} performance under load',
        'description': 'Test {} response time with multiple concurrent users',
        'preconditions': 'System is running with test data loaded',
        'test_type': 'Performance',
        'priority': 'P2'
    },
    {
        'title': 'Verify {} security controls',
        'description': 'Test that {} properly enforces security policies',
        'preconditions': 'System is running with security enabled',
        'test_type': 'Security',
        'priority': 'P0'
    },
    {
        'title': 'Verify {} integration with {}',
        'description': 'Test that {} correctly integrates with {}',
        'preconditions': 'Both systems are running and connected',
        'test_type': 'Integration',
        'priority': 'P1'
    },
    {
        'title': 'Verify {} UI responsiveness',
        'description': 'Test that {} UI is responsive on different screen sizes',
        'preconditions': 'Application is accessible',
        'test_type': 'Usability',
        'priority': 'P2'
    },
    {
        'title': 'Smoke test for {} module',
        'description': 'Quick verification that {} basic functionality works',
        'preconditions': 'System is deployed',
        'test_type': 'Smoke',
        'priority': 'P0'
    },
    {
        'title': 'Regression test for {} after update',
        'description': 'Verify {} still works after recent changes',
        'preconditions': 'System is updated to latest version',
        'test_type': 'Regression',
        'priority': 'P1'
    }
]

FEATURES = [
    'user authentication', 'password reset', 'user profile', 'dashboard',
    'project creation', 'task management', 'bug tracking', 'reporting',
    'notifications', 'search functionality', 'data export', 'user permissions',
    'API endpoints', 'file upload', 'email service', 'database queries'
]

def generate_test_run_id(index):
    """Generate test run ID"""
    return f"TR-{index:03d}"

def generate_test_id(index):
    """Generate test case ID"""
    return f"TC-{index:03d}"

def generate_execution_id(index):
    """Generate test execution ID"""
    return f"TE-{index:03d}"

def generate_bug_id(index):
    """Generate bug ID"""
    return f"BUG-QA-{index:03d}"

def generate_test_runs(count=20):
    """Generate test runs distributed across hierarchy levels"""
    test_runs = []
    
    # Distribution across hierarchy: 5 Project, 5 UseCase, 4 UserStory, 4 Task, 2 Subtask
    hierarchy_distribution = (
        [('project', PROJECTS[0])] * 5 +
        [('usecase', USECASES[0])] * 5 +
        [('user_story', USER_STORIES[0])] * 4 +
        [('task', TASKS[0])] * 4 +
        [('subtask', SUBTASKS[0])] * 2
    )
    
    test_run_names = [
        'Login Module Test Suite',
        'User Management Regression',
        'API Integration Tests',
        'Dashboard Functionality',
        'Security Audit Tests',
        'Performance Benchmarking',
        'Mobile Responsiveness',
        'Data Export Features',
        'Notification System',
        'Search Functionality',
        'Permission Controls',
        'File Upload Tests',
        'Email Service Tests',
        'Database Operations',
        'UI Component Tests',
        'End-to-End Workflows',
        'Cross-Browser Testing',
        'Accessibility Tests',
        'Smoke Test Suite',
        'Acceptance Tests'
    ]
    
    components = [
        'Authentication Module', 'User Management', 'API Gateway', 'Dashboard',
        'Security Layer', 'Performance Monitor', 'Mobile UI', 'Export Service',
        'Notification Service', 'Search Engine', 'Permission System', 'File Storage',
        'Email Service', 'Database Layer', 'UI Components', 'Workflow Engine',
        'Browser Compatibility', 'Accessibility Features', 'Core Features', 'Business Logic'
    ]
    
    end_date = datetime.now()
    
    for i in range(count):
        # Determine hierarchy level
        if i < len(hierarchy_distribution):
            hierarchy_type, hierarchy_id = hierarchy_distribution[i]
        else:
            hierarchy_type, hierarchy_id = random.choice(hierarchy_distribution)
        
        # Generate dates (test runs from past 60 days)
        days_ago = random.randint(0, 60)
        start_date = end_date - timedelta(days=days_ago)
        
        # Determine status and end date
        status = random.choice(['In Progress'] * 3 + ['Completed'] * 6 + ['Aborted'] * 1)
        if status == 'Completed':
            duration = random.randint(3, 14)
            end_date_val = start_date + timedelta(days=duration)
        elif status == 'Aborted':
            duration = random.randint(1, 5)
            end_date_val = start_date + timedelta(days=duration)
        else:
            end_date_val = None
        
        run_type = random.choice(TEST_RUN_TYPES)
        
        test_run = {
            'ID': generate_test_run_id(i + 1),
            'Project ID': hierarchy_id if hierarchy_type == 'project' else '',
            'Use Case ID': hierarchy_id if hierarchy_type == 'usecase' else '',
            'User Story ID': hierarchy_id if hierarchy_type == 'user_story' else '',
            'Task ID': hierarchy_id if hierarchy_type == 'task' else '',
            'Subtask ID': hierarchy_id if hierarchy_type == 'subtask' else '',
            'Name': test_run_names[i] if i < len(test_run_names) else f'Test Run {i+1}',
            'Purpose': f'Verify {test_run_names[i].lower()} functionality' if i < len(test_run_names) else f'Test run purpose {i+1}',
            'Short Description': f'Comprehensive testing of {components[i].lower()}' if i < len(components) else f'Test run {i+1}',
            'Long Description': f'This test run covers all aspects of {components[i].lower()} including functionality, performance, and edge cases.' if i < len(components) else f'Detailed description for test run {i+1}',
            'Component Attached To': components[i] if i < len(components) else f'Component {i+1}',
            'Run Type': run_type,
            'Status': status,
            'Start Date': start_date.strftime('%Y-%m-%d'),
            'End Date': end_date_val.strftime('%Y-%m-%d') if end_date_val else '',
            'Created By': random.choice(USERS)
        }
        
        test_runs.append(test_run)
    
    return test_runs

def generate_test_steps(feature, num_steps=None):
    """Generate realistic test steps"""
    if num_steps is None:
        num_steps = random.randint(3, 7)
    
    steps = []
    steps.append(f"Navigate to {feature} page")
    
    for i in range(num_steps - 2):
        actions = [
            f"Enter test data in {random.choice(['input field', 'form', 'text box'])}",
            f"Click {random.choice(['Submit', 'Save', 'Update', 'Delete', 'Cancel'])} button",
            f"Select option from {random.choice(['dropdown', 'menu', 'list'])}",
            f"Verify {random.choice(['data is displayed', 'message appears', 'page loads'])}",
            f"Check {random.choice(['validation', 'error handling', 'success message'])}"
        ]
        steps.append(random.choice(actions))
    
    steps.append(f"Verify {feature} completes successfully")
    
    return json.dumps(steps)

def generate_test_cases(test_runs, count=50):
    """Generate test cases linked to test runs"""
    test_cases = []
    
    # Distribute test cases across test runs (2-3 test cases per run on average)
    for i in range(count):
        template = random.choice(TEST_CASE_TEMPLATES)
        feature = random.choice(FEATURES)
        feature2 = random.choice([f for f in FEATURES if f != feature])
        
        # Select a random test run
        test_run = random.choice(test_runs)
        
        # Determine status based on test run status
        if test_run['Status'] == 'Completed':
            status = random.choice(['Passed'] * 6 + ['Failed'] * 2 + ['Blocked'] * 1 + ['Skipped'] * 1)
        elif test_run['Status'] == 'In Progress':
            status = random.choice(['Not Executed'] * 4 + ['Passed'] * 3 + ['Failed'] * 2 + ['Blocked'] * 1)
        else:  # Aborted
            status = random.choice(['Not Executed'] * 7 + ['Blocked'] * 3)
        
        # Generate execution details if executed
        executed_by = ''
        executed_at = ''
        actual_result = ''
        inference = ''
        
        if status != 'Not Executed':
            executed_by = random.choice(USERS)
            # Execution date should be after test run start date
            test_run_start = datetime.strptime(test_run['Start Date'], '%Y-%m-%d')
            if test_run['End Date']:
                test_run_end = datetime.strptime(test_run['End Date'], '%Y-%m-%d')
                days_range = (test_run_end - test_run_start).days
                exec_days = random.randint(0, max(1, days_range))
                executed_at = (test_run_start + timedelta(days=exec_days)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                executed_at = (test_run_start + timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate actual result and inference
            if status == 'Passed':
                actual_result = f"Test passed successfully. {feature.capitalize()} worked as expected."
                inference = "All test steps completed successfully. No issues found."
            elif status == 'Failed':
                actual_result = f"Test failed: {random.choice(['Expected behavior not observed', 'Error message displayed', 'Function returned incorrect result'])}"
                inference = "Bug found and reported. Requires investigation and fix."
            elif status == 'Blocked':
                actual_result = f"Test blocked: {random.choice(['Test environment unavailable', 'Dependent service is down', 'Prerequisites not met'])}"
                inference = "Cannot proceed with testing until blocker is resolved."
            elif status == 'Skipped':
                actual_result = "Test skipped due to time constraints"
                inference = "Will be executed in next test cycle."
        
        test_case = {
            'ID': generate_test_id(i + 1),
            'Test Run ID': test_run['ID'],
            'Test Case Name': template['title'].format(feature, feature2) if '{}' in template['title'] and template['title'].count('{}') > 1 else template['title'].format(feature),
            'Test Case Description': template['description'].format(feature, feature2) if '{}' in template['description'] and template['description'].count('{}') > 1 else template['description'].format(feature),
            'Test Case Steps': generate_test_steps(feature),
            'Expected Result': f"{feature.capitalize()} completes successfully with expected output",
            'Actual Result': actual_result,
            'Inference': inference,
            'Component Attached To': test_run['Component Attached To'],
            'Remarks': '',
            'Priority': template['priority'],
            'Status': status,
            'Executed By': executed_by,
            'Executed At': executed_at,
            'Created By': random.choice(USERS)
        }
        
        test_cases.append(test_case)
    
    return test_cases

def generate_test_executions(test_cases, count=100):
    """Generate test executions with realistic distribution"""
    executions = []
    
    # Distribution: 60% Passed, 25% Failed, 10% Blocked, 5% Skipped
    status_distribution = (
        ['Passed'] * 60 +
        ['Failed'] * 25 +
        ['Blocked'] * 10 +
        ['Skipped'] * 5
    )
    
    # Generate executions over the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for i in range(count):
        test_case = random.choice(test_cases)
        status = random.choice(status_distribution)
        
        # Random execution date in the past 30 days
        days_ago = random.randint(0, 30)
        execution_date = end_date - timedelta(days=days_ago)
        
        browser = random.choice(BROWSERS)
        os = random.choice(OPERATING_SYSTEMS)
        device = random.choice(DEVICE_TYPES)
        
        execution = {
            'ID': generate_execution_id(i + 1),
            'Test Case ID': test_case['ID'],
            'Test Run ID': '',
            'Executed By': random.choice(USERS),
            'Execution Date': execution_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Execution Status': status,
            'Actual Result': generate_actual_result(status, test_case['Title']),
            'Execution Notes': generate_execution_notes(status),
            'Environment': f"{browser}, {os}",
            'Browser': browser,
            'OS': os,
            'Device Type': device,
            'Screenshots': json.dumps(['screenshot.png'] if status == 'Failed' else []),
            'Log Files': json.dumps(['error.log'] if status in ['Failed', 'Blocked'] else [])
        }
        
        executions.append(execution)
    
    return executions

def generate_actual_result(status, title):
    """Generate actual result based on execution status"""
    if status == 'Passed':
        return f"Test passed successfully. {title} worked as expected."
    elif status == 'Failed':
        failures = [
            "Expected behavior not observed",
            "Error message displayed",
            "Function returned incorrect result",
            "UI element not responding",
            "Data not saved correctly"
        ]
        return f"Test failed: {random.choice(failures)}"
    elif status == 'Blocked':
        blockers = [
            "Test environment unavailable",
            "Dependent service is down",
            "Test data not available",
            "Prerequisites not met"
        ]
        return f"Test blocked: {random.choice(blockers)}"
    elif status == 'Skipped':
        return "Test skipped due to time constraints"
    else:
        return "Test not applicable in current context"

def generate_execution_notes(status):
    """Generate execution notes"""
    if status == 'Passed':
        return random.choice([
            "Test executed smoothly",
            "No issues encountered",
            "All steps completed successfully",
            "Verified on first attempt"
        ])
    elif status == 'Failed':
        return random.choice([
            "Bug found and reported",
            "Issue requires investigation",
            "Failure is reproducible",
            "Multiple attempts failed"
        ])
    elif status == 'Blocked':
        return random.choice([
            "Waiting for environment fix",
            "Blocked by infrastructure issue",
            "Cannot proceed without dependencies",
            "Will retry after resolution"
        ])
    else:
        return "Standard execution notes"

def generate_bugs(test_cases, count=60):
    """Generate bugs with various statuses and severities
    40 bugs from test cases, 20 bugs created directly
    """
    bugs = []
    
    # 40 bugs linked to test cases (from failed tests)
    # 20 bugs created directly at hierarchy levels
    linked_bug_count = 40
    direct_bug_count = 20
    
    # Status distribution for realistic lifecycle
    status_weights = {
        'New': 10,
        'Open': 15,
        'In Progress': 20,
        'Fixed': 15,
        'Ready for Testing': 10,
        'Verified': 10,
        'Closed': 15,
        'Reopened': 3,
        'Deferred': 2
    }
    
    # Generate bugs over the past 90 days
    end_date = datetime.now()
    
    # Get failed test cases for linking
    failed_test_cases = [tc for tc in test_cases if tc['Status'] == 'Failed']
    
    for i in range(count):
        # Determine if this bug is linked to a test case
        is_linked = i < linked_bug_count and len(failed_test_cases) > 0
        
        test_run_id = ''
        test_case_id = ''
        component = ''
        
        if is_linked:
            # Link to a failed test case
            test_case = random.choice(failed_test_cases)
            test_case_id = test_case['ID']
            test_run_id = test_case['Test Run ID']
            component = test_case['Component Attached To']
            
            # For linked bugs, don't set hierarchy fields
            hierarchy_type = None
            hierarchy_id = None
        else:
            # Direct bug - select hierarchy level
            hierarchy_options = [
                ('project', PROJECTS[0]),
                ('usecase', USECASES[0]),
                ('user_story', USER_STORIES[0]),
                ('task', TASKS[0]),
                ('subtask', SUBTASKS[0])
            ]
            hierarchy_type, hierarchy_id = random.choice(hierarchy_options)
            component = random.choice([
                'Authentication Module', 'User Management', 'API Gateway', 'Dashboard',
                'Security Layer', 'Performance Monitor', 'Mobile UI', 'Export Service'
            ])
        
        # Select status based on weights
        status = random.choices(
            list(status_weights.keys()),
            weights=list(status_weights.values())
        )[0]
        
        # Determine resolution type for closed bugs
        resolution_type = ''
        if status in ['Fixed', 'Verified', 'Closed']:
            resolution_type = random.choice(['Fixed', 'Fixed', 'Fixed', 'Duplicate', 'Cannot Reproduce'])
        elif status == 'Deferred':
            resolution_type = 'Deferred'
        
        # Generate bug age (older bugs more likely to be closed)
        if status in ['Closed', 'Verified']:
            days_ago = random.randint(30, 90)
        elif status in ['New', 'Open']:
            days_ago = random.randint(0, 15)
        else:
            days_ago = random.randint(5, 45)
        
        severity = random.choice(BUG_SEVERITIES)
        priority = random.choice(BUG_PRIORITIES)
        bug_type = random.choice(BUG_TYPES)
        
        # Generate creation date
        created_at = end_date - timedelta(days=days_ago)
        
        # Generate closed date for closed bugs
        closed_at = ''
        if status in ['Closed', 'Verified']:
            close_days = random.randint(5, days_ago) if days_ago > 5 else days_ago
            closed_at = (end_date - timedelta(days=close_days)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate reproduction steps
        if is_linked and test_case_id:
            # Use test case steps as reproduction steps
            reproduction_steps = f"Follow test case {test_case_id} steps:\n{test_case['Test Case Steps'][:200]}..."
            expected_result = test_case['Expected Result']
            actual_result = test_case['Actual Result']
        else:
            reproduction_steps = generate_reproduction_steps(bug_type)
            expected_result = generate_expected_result(bug_type)
            actual_result = generate_actual_result_bug(bug_type)
        
        bug = {
            'ID': generate_bug_id(i + 1),
            'Test Run ID': test_run_id,
            'Test Case ID': test_case_id,
            'Project ID': hierarchy_id if hierarchy_type == 'project' else '',
            'Use Case ID': hierarchy_id if hierarchy_type == 'usecase' else '',
            'User Story ID': hierarchy_id if hierarchy_type == 'user_story' else '',
            'Task ID': hierarchy_id if hierarchy_type == 'task' else '',
            'Subtask ID': hierarchy_id if hierarchy_type == 'subtask' else '',
            'Title': generate_bug_title(bug_type, severity),
            'Short Description': generate_bug_short_description(bug_type),
            'Long Description': generate_bug_long_description(bug_type, severity),
            'Category': bug_type,
            'Severity': severity,
            'Priority': priority,
            'Status': status,
            'Reporter ID': random.choice(USERS),
            'Assignee ID': random.choice(USERS) if status not in ['New', 'Deferred'] else '',
            'QA Owner ID': random.choice(USERS),
            'Reproduction Steps': reproduction_steps,
            'Expected Result': expected_result,
            'Actual Result': actual_result,
            'Component Attached To': component,
            'Environment': random.choice(['Production', 'Staging', 'Development', 'QA']),
            'Linked Task ID': random.choice(TASKS + ['']) if not is_linked else '',
            'Linked Commit': f"abc{random.randint(1000, 9999)}def" if resolution_type == 'Fixed' and random.random() < 0.5 else '',
            'Linked PR': f"https://github.com/company/worky/pull/{random.randint(100, 999)}" if resolution_type == 'Fixed' and random.random() < 0.3 else '',
            'Reopen Count': random.randint(0, 2) if status == 'Reopened' else 0,
            'Resolution Notes': generate_resolution_notes(resolution_type) if resolution_type else '',
            'Created At': created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Closed At': closed_at
        }
        
        bugs.append(bug)
    
    return bugs

def generate_bug_title(bug_type, severity):
    """Generate realistic bug title"""
    titles_by_type = {
        'Functional': [
            'Login fails with valid credentials',
            'Data not saving correctly',
            'Search returns incorrect results',
            'Form validation not working',
            'Button click has no effect'
        ],
        'Performance': [
            'Page load time exceeds 5 seconds',
            'API response time too slow',
            'Database query timeout',
            'Memory leak in background process',
            'UI freezes during data load'
        ],
        'Security': [
            'SQL injection vulnerability found',
            'XSS attack possible in input field',
            'Unauthorized access to admin panel',
            'Password stored in plain text',
            'Session token not expiring'
        ],
        'UI/UX': [
            'Button not visible on mobile',
            'Text overlapping on small screens',
            'Inconsistent color scheme',
            'Navigation menu not responsive',
            'Form fields misaligned'
        ],
        'Data': [
            'Data corruption in database',
            'Incorrect data type in field',
            'Missing required field validation',
            'Data export contains wrong values',
            'Duplicate records created'
        ],
        'Integration': [
            'API integration failing',
            'Third-party service not responding',
            'Webhook not triggering',
            'SSO authentication broken',
            'Email service integration error'
        ],
        'Configuration': [
            'Environment variable not set',
            'Configuration file missing',
            'Wrong database connection string',
            'SSL certificate expired',
            'Port conflict in deployment'
        ]
    }
    
    return random.choice(titles_by_type.get(bug_type, titles_by_type['Functional']))

def generate_bug_short_description(bug_type):
    """Generate short bug description"""
    descriptions = {
        'Functional': 'Feature not working as expected',
        'Performance': 'System performance degraded',
        'Security': 'Security vulnerability identified',
        'UI/UX': 'User interface issue',
        'Data': 'Data integrity problem',
        'Integration': 'Integration failure',
        'Configuration': 'Configuration issue'
    }
    return descriptions.get(bug_type, 'Issue found in system')

def generate_bug_long_description(bug_type, severity):
    """Generate detailed bug description"""
    base_descriptions = {
        'Functional': 'The functionality is not working as specified in the requirements. Users are unable to complete the intended action.',
        'Performance': 'The system is experiencing performance issues that impact user experience. Response times are significantly slower than acceptable.',
        'Security': 'A security vulnerability has been identified that could potentially be exploited. Immediate attention required.',
        'UI/UX': 'The user interface has visual or usability issues that affect the user experience.',
        'Data': 'Data is not being handled correctly, leading to potential data integrity issues.',
        'Integration': 'The integration with external systems or services is not functioning properly.',
        'Configuration': 'System configuration is incorrect or missing, preventing proper operation.'
    }
    
    severity_additions = {
        'Blocker': ' This is blocking all testing and must be fixed immediately.',
        'Critical': ' This severely impacts core functionality and requires urgent attention.',
        'Major': ' This significantly affects functionality and should be prioritized.',
        'Minor': ' This is a minor issue that should be addressed when possible.',
        'Trivial': ' This is a cosmetic issue with minimal impact.'
    }
    
    base = base_descriptions.get(bug_type, 'An issue has been identified.')
    addition = severity_additions.get(severity, '')
    
    return base + addition

def generate_reproduction_steps(bug_type):
    """Generate reproduction steps for direct bugs"""
    steps_by_type = {
        'Functional': '1. Navigate to the feature page\n2. Enter test data\n3. Click submit button\n4. Observe the error',
        'Performance': '1. Open the application\n2. Navigate to the slow page\n3. Measure load time\n4. Observe delay',
        'Security': '1. Attempt unauthorized access\n2. Try to bypass security\n3. Observe vulnerability',
        'UI/UX': '1. Open the page on mobile device\n2. Observe layout issues\n3. Try to interact with elements',
        'Data': '1. Create new record\n2. Save data\n3. Refresh page\n4. Observe data corruption',
        'Integration': '1. Trigger integration\n2. Check external service\n3. Observe failure',
        'Configuration': '1. Check configuration file\n2. Verify settings\n3. Observe incorrect values'
    }
    return steps_by_type.get(bug_type, '1. Perform action\n2. Observe issue')

def generate_expected_result(bug_type):
    """Generate expected result for bugs"""
    results = {
        'Functional': 'Feature should work correctly and complete the action',
        'Performance': 'Page should load within acceptable time (< 2 seconds)',
        'Security': 'Security controls should prevent unauthorized access',
        'UI/UX': 'UI should display correctly on all devices',
        'Data': 'Data should be saved and retrieved correctly',
        'Integration': 'Integration should work seamlessly',
        'Configuration': 'Configuration should be correct and valid'
    }
    return results.get(bug_type, 'System should work as expected')

def generate_actual_result_bug(bug_type):
    """Generate actual result for bugs"""
    results = {
        'Functional': 'Feature fails to complete the action, error displayed',
        'Performance': 'Page takes 5+ seconds to load',
        'Security': 'Unauthorized access is possible',
        'UI/UX': 'UI elements are misaligned or not visible',
        'Data': 'Data is corrupted or not saved',
        'Integration': 'Integration fails with error',
        'Configuration': 'Configuration is missing or incorrect'
    }
    return results.get(bug_type, 'System does not work as expected')

def generate_resolution_notes(resolution_type):
    """Generate resolution notes"""
    notes = {
        'Fixed': 'Issue has been fixed and verified. Code changes deployed to production.',
        'Duplicate': 'This is a duplicate of an existing bug. Closing as duplicate.',
        'Cannot Reproduce': 'Unable to reproduce the issue with provided steps. Needs more information.',
        "Won't Fix": 'After review, decided not to fix this issue due to low priority and impact.',
        'By Design': 'This behavior is by design and working as intended.',
        'Deferred': 'Issue deferred to future release due to time constraints.'
    }
    return notes.get(resolution_type, '')

def generate_comment_id(index):
    """Generate comment ID"""
    return f"CMT-{index:03d}"

def generate_status_history_id(index):
    """Generate status history ID"""
    return f"SH-{index:03d}"

def generate_bug_comments(bugs, count=100):
    """Generate comments for bugs"""
    comments = []
    
    comment_templates = [
        "I've investigated this issue and found the root cause. {}",
        "This is related to the recent changes in {}. We should review that code.",
        "Can someone verify if this is still reproducible in the latest build?",
        "I've assigned this to {} for investigation.",
        "This needs to be prioritized for the next sprint.",
        "I've added more details in the description. Please review.",
        "This is a duplicate of another bug we fixed last week.",
        "The fix has been deployed to staging. Ready for testing.",
        "Verified the fix in production. Working as expected now.",
        "We need to add regression tests for this scenario.",
        "This is affecting multiple users. Increasing priority.",
        "I've attached screenshots showing the issue.",
        "The workaround is to {}. We'll fix this properly in the next release.",
        "This is by design according to the requirements document.",
        "We should defer this to the next release due to time constraints.",
        "@{} Can you take a look at this?",
        "I've reproduced this on my local environment.",
        "This only happens on {} browser. Works fine on others.",
        "The issue is in the {} module. I'll create a fix.",
        "This was introduced in version {}. We need to rollback or hotfix."
    ]
    
    details = [
        "the database connection pooling",
        "the authentication service",
        "the API endpoint",
        "the frontend component",
        "the validation logic"
    ]
    
    end_date = datetime.now()
    
    # Generate comments for random bugs
    for i in range(count):
        bug = random.choice(bugs)
        
        # Comments should be after bug creation (use bug age)
        # Bugs are created 0-90 days ago, comments should be within that range
        max_days_ago = 90
        comment_days_ago = random.randint(0, max_days_ago)
        comment_date = end_date - timedelta(days=comment_days_ago)
        
        template = random.choice(comment_templates)
        
        # Fill in template placeholders
        if '{}' in template:
            if '@{}' in template:
                comment_text = template.format(random.choice(USERS))
            else:
                comment_text = template.format(random.choice(details))
        else:
            comment_text = template
        
        comment = {
            'ID': generate_comment_id(i + 1),
            'Bug ID': bug['ID'],
            'Test Case ID': '',
            'Comment Text': comment_text,
            'Author ID': random.choice(USERS),
            'Mentioned Users': json.dumps([random.choice(USERS)]) if '@' in comment_text else json.dumps([]),
            'Is Edited': random.choice([False] * 9 + [True]),
            'Edited At': (comment_date + timedelta(minutes=random.randint(1, 14))).strftime('%Y-%m-%d %H:%M:%S') if random.random() < 0.1 else '',
            'Attachments': json.dumps(['screenshot.png'] if random.random() < 0.2 else []),
            'Created At': comment_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        comments.append(comment)
    
    return comments

def generate_test_case_comments(test_cases, count=30):
    """Generate comments for test cases"""
    comments = []
    
    comment_templates = [
        "This test case needs to be updated to reflect the new requirements.",
        "I've added more detailed test steps for clarity.",
        "This test is failing consistently. We should investigate.",
        "Can we add more edge cases to this test?",
        "This test case is redundant with TC-{}. Should we merge them?",
        "The expected result needs to be more specific.",
        "I've updated the test data to use more realistic values.",
        "This test should be marked as P0 priority.",
        "We need to automate this test case.",
        "The preconditions are not clear. Please clarify.",
        "This test case covers the happy path. We need negative tests too.",
        "I've verified this test case with the product owner.",
        "This test is blocked by the bug BUG-QA-{}.",
        "We should add this to the smoke test suite.",
        "The test steps are too vague. Adding more details.",
        "This test case is deprecated. We should archive it.",
        "I've executed this test and it passed. Marking as approved.",
        "We need to review this test case in the next sprint planning.",
        "This test requires special test data setup.",
        "The test environment needs to be configured before running this."
    ]
    
    end_date = datetime.now()
    
    for i in range(count):
        test_case = random.choice(test_cases)
        
        comment_days_ago = random.randint(0, 30)
        comment_date = end_date - timedelta(days=comment_days_ago)
        
        template = random.choice(comment_templates)
        
        # Fill in template placeholders
        if '{}' in template:
            comment_text = template.format(random.randint(1, 30))
        else:
            comment_text = template
        
        comment = {
            'ID': generate_comment_id(len(comments) + 101),  # Continue from bug comments
            'Bug ID': '',
            'Test Case ID': test_case['ID'],
            'Comment Text': comment_text,
            'Author ID': random.choice(USERS),
            'Mentioned Users': json.dumps([]),
            'Is Edited': False,
            'Edited At': '',
            'Attachments': json.dumps([]),
            'Created At': comment_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        comments.append(comment)
    
    return comments

def generate_bug_status_history(bugs):
    """Generate status history for bugs showing realistic lifecycle"""
    history = []
    history_id = 1
    
    # Status transition rules
    status_transitions = {
        'New': ['Open', 'Deferred', 'Rejected'],
        'Open': ['In Progress', 'Deferred'],
        'In Progress': ['Fixed', 'Open', 'Blocked'],
        'Fixed': ['Ready for Testing', 'Reopened'],
        'Ready for Testing': ['Retest', 'Reopened'],
        'Retest': ['Verified', 'Reopened'],
        'Verified': ['Closed', 'Reopened'],
        'Closed': ['Reopened'],
        'Reopened': ['In Progress', 'Open'],
        'Deferred': ['Open'],
        'Rejected': []
    }
    
    end_date = datetime.now()
    
    for bug in bugs:
        current_status = bug['Status']
        
        # Generate history leading to current status
        # Start from 'New' and transition to current status
        if current_status == 'New':
            continue  # No history for new bugs
        
        # Build a realistic path to current status
        status_path = ['New']
        
        if current_status in ['Open', 'In Progress', 'Fixed', 'Ready for Testing', 'Verified', 'Closed']:
            # Normal progression
            if current_status != 'Open':
                status_path.append('Open')
            if current_status in ['In Progress', 'Fixed', 'Ready for Testing', 'Verified', 'Closed']:
                status_path.append('In Progress')
            if current_status in ['Fixed', 'Ready for Testing', 'Verified', 'Closed']:
                status_path.append('Fixed')
            if current_status in ['Ready for Testing', 'Verified', 'Closed']:
                status_path.append('Ready for Testing')
            if current_status in ['Verified', 'Closed']:
                status_path.append('Verified')
            if current_status == 'Closed':
                status_path.append('Closed')
        elif current_status == 'Reopened':
            status_path.extend(['Open', 'In Progress', 'Fixed', 'Verified', 'Closed', 'Reopened'])
        elif current_status == 'Deferred':
            status_path.extend(['Open', 'Deferred'])
        elif current_status == 'Rejected':
            status_path.extend(['Open', 'Rejected'])
        
        # Generate history entries for each transition
        # Spread transitions over time (bugs created 0-90 days ago)
        max_days_ago = 90
        days_per_transition = max_days_ago // len(status_path) if len(status_path) > 1 else 1
        
        for i in range(1, len(status_path)):
            from_status = status_path[i - 1]
            to_status = status_path[i]
            
            # Calculate transition date
            transition_days_ago = max_days_ago - (i * days_per_transition)
            transition_date = end_date - timedelta(days=max(0, transition_days_ago))
            
            # Generate notes for transition
            notes = generate_status_transition_notes(from_status, to_status)
            
            # Determine resolution type
            resolution_type = ''
            if to_status in ['Fixed', 'Verified', 'Closed']:
                resolution_type = 'Fixed'
            elif to_status == 'Deferred':
                resolution_type = 'Deferred'
            elif to_status == 'Rejected':
                resolution_type = "Won't Fix"
            
            history_entry = {
                'ID': generate_status_history_id(history_id),
                'Bug ID': bug['ID'],
                'From Status': from_status,
                'To Status': to_status,
                'Resolution Type': resolution_type,
                'Notes': notes,
                'Changed By': random.choice(USERS),
                'Changed At': transition_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            history.append(history_entry)
            history_id += 1
    
    return history

def generate_status_transition_notes(from_status, to_status):
    """Generate notes for status transitions"""
    transition_notes = {
        ('New', 'Open'): 'Bug confirmed and opened for investigation',
        ('Open', 'In Progress'): 'Started working on the fix',
        ('In Progress', 'Fixed'): 'Fix implemented and ready for testing',
        ('Fixed', 'Ready for Testing'): 'Fix deployed to test environment',
        ('Ready for Testing', 'Retest'): 'Initial test failed, needs retest',
        ('Retest', 'Verified'): 'Fix verified in test environment',
        ('Verified', 'Closed'): 'Fix verified in production, closing bug',
        ('Closed', 'Reopened'): 'Issue reoccurred, reopening for investigation',
        ('Reopened', 'In Progress'): 'Investigating the reopened issue',
        ('Open', 'Deferred'): 'Deferring to next release due to priority',
        ('New', 'Rejected'): 'Not a bug, working as designed',
        ('Deferred', 'Open'): 'Reopening deferred bug for current sprint'
    }
    
    key = (from_status, to_status)
    return transition_notes.get(key, f'Status changed from {from_status} to {to_status}')

def generate_bug_assignments(bugs):
    """Generate assignment history for bugs"""
    assignments = []
    
    # For bugs that are assigned, create assignment records
    for bug in bugs:
        if bug['Assignee ID']:
            # Create assignment record
            # Assignment happened shortly after bug was opened
            end_date = datetime.now()
            assignment_days_ago = random.randint(0, 85)  # Slightly before current date
            assignment_date = end_date - timedelta(days=assignment_days_ago)
            
            assignment = {
                'Bug ID': bug['ID'],
                'Assigned To': bug['Assignee ID'],
                'Assigned By': random.choice(USERS),
                'Assigned At': assignment_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Notes': f"Assigned to {bug['Assignee ID']} for investigation and resolution"
            }
            
            assignments.append(assignment)
    
    return assignments

def save_qa_data():
    """Generate and save all QA data"""
    print("Generating QA dummy data...")
    print("Following QA Testing and Bug Management spec requirements")
    print()
    
    # Ensure excel_templates directory exists
    os.makedirs(EXCEL_DIR, exist_ok=True)
    
    # Generate test runs
    print("Generating 20 test runs across hierarchy levels...")
    test_runs = generate_test_runs(20)
    test_runs_file = os.path.join(EXCEL_DIR, 'test_runs.xlsx')
    df_test_runs = pd.DataFrame(test_runs)
    df_test_runs.to_excel(test_runs_file, index=False, sheet_name='Test Runs')
    print(f"✓ Created {len(test_runs)} test runs")
    print(f"  - Project level: {sum(1 for tr in test_runs if tr['Project ID'])}")
    print(f"  - Use Case level: {sum(1 for tr in test_runs if tr['Use Case ID'])}")
    print(f"  - User Story level: {sum(1 for tr in test_runs if tr['User Story ID'])}")
    print(f"  - Task level: {sum(1 for tr in test_runs if tr['Task ID'])}")
    print(f"  - Subtask level: {sum(1 for tr in test_runs if tr['Subtask ID'])}")
    print()
    
    # Generate test cases
    print("Generating 50 test cases within test runs...")
    test_cases = generate_test_cases(test_runs, 50)
    test_cases_file = os.path.join(EXCEL_DIR, 'test_cases.xlsx')
    df_test_cases = pd.DataFrame(test_cases)
    df_test_cases.to_excel(test_cases_file, index=False, sheet_name='Test Cases')
    
    # Count test case statuses
    tc_status_counts = {}
    for tc in test_cases:
        status = tc['Status']
        tc_status_counts[status] = tc_status_counts.get(status, 0) + 1
    
    print(f"✓ Created {len(test_cases)} test cases")
    for status, count in sorted(tc_status_counts.items()):
        print(f"  - {status}: {count}")
    print()
    
    # Generate bugs
    print("Generating 60 bugs (40 from test cases, 20 direct)...")
    bugs = generate_bugs(test_cases, 60)
    bugs_file = os.path.join(EXCEL_DIR, 'bugs_extended.xlsx')
    df_bugs = pd.DataFrame(bugs)
    df_bugs.to_excel(bugs_file, index=False, sheet_name='Bugs Extended')
    
    # Count bug statuses and severities
    bug_status_counts = {}
    bug_severity_counts = {}
    for bug in bugs:
        status = bug['Status']
        severity = bug['Severity']
        bug_status_counts[status] = bug_status_counts.get(status, 0) + 1
        bug_severity_counts[severity] = bug_severity_counts.get(severity, 0) + 1
    
    print(f"✓ Created {len(bugs)} bugs")
    print("  Status distribution:")
    for status, count in sorted(bug_status_counts.items()):
        print(f"    - {status}: {count}")
    print("  Severity distribution:")
    for severity, count in sorted(bug_severity_counts.items()):
        print(f"    - {severity}: {count}")
    print()
    
    # Generate bug comments
    print("Generating 100+ comments...")
    bug_comments = generate_bug_comments(bugs, 100)
    test_case_comments = generate_test_case_comments(test_cases, 30)
    all_comments = bug_comments + test_case_comments
    comments_file = os.path.join(EXCEL_DIR, 'comments.xlsx')
    df_comments = pd.DataFrame(all_comments)
    df_comments.to_excel(comments_file, index=False, sheet_name='Comments')
    print(f"✓ Created {len(all_comments)} comments")
    print(f"  - Bug comments: {len(bug_comments)}")
    print(f"  - Test case comments: {len(test_case_comments)}")
    print()
    
    # Generate bug status history
    print("Generating bug status history...")
    status_history = generate_bug_status_history(bugs)
    history_file = os.path.join(EXCEL_DIR, 'bug_status_history.xlsx')
    df_history = pd.DataFrame(status_history)
    df_history.to_excel(history_file, index=False, sheet_name='Status History')
    print(f"✓ Created {len(status_history)} status history entries")
    print()
    
    # Generate bug assignments
    print("Generating bug assignments...")
    assignments = generate_bug_assignments(bugs)
    assignments_file = os.path.join(EXCEL_DIR, 'bug_assignments.xlsx')
    df_assignments = pd.DataFrame(assignments)
    df_assignments.to_excel(assignments_file, index=False, sheet_name='Assignments')
    print(f"✓ Created {len(assignments)} bug assignments")
    assigned_count = sum(1 for bug in bugs if bug['Assignee ID'])
    print(f"  - {assigned_count} bugs assigned to users")
    print()
    
    print("=" * 60)
    print("QA dummy data generated successfully!")
    print()
    print("Summary:")
    print(f"  - {len(test_runs)} test runs")
    print(f"  - {len(test_cases)} test cases")
    print(f"  - {len(bugs)} bugs ({sum(1 for b in bugs if b['Test Case ID'])} from test cases, {sum(1 for b in bugs if not b['Test Case ID'])} direct)")
    print(f"  - {len(all_comments)} comments")
    print(f"  - {len(status_history)} status history entries")
    print(f"  - {len(assignments)} bug assignments")
    print()
    print("Files created:")
    print(f"  - {test_runs_file}")
    print(f"  - {test_cases_file}")
    print(f"  - {bugs_file}")
    print(f"  - {comments_file}")
    print(f"  - {history_file}")
    print(f"  - {assignments_file}")
    print()
    print("Next steps:")
    print("  1. Review the generated data in excel_templates/")
    print("  2. Run: python3 load_qa_data.py (to load into database)")
    print("=" * 60)

if __name__ == '__main__':
    save_qa_data()

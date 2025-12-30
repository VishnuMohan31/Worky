"""
Create sample dummy data in Excel files
"""
import os
import pandas as pd
from config import EXCEL_DIR

# Sample data
clients_data = [{
    'ID': 'CLI-001',
    'Name': 'DataLegos Inc',
    'Short Description': 'Leading data analytics company',
    'Long Description': 'DataLegos is a premier data analytics and business intelligence company.',
    'Is Active': True
}]

users_data = [{
    'ID': 'USR-001',
    'Email': 'admin@datalegos.com',
    'Password': 'password',
    'Full Name': 'Admin User',
    'Role': 'Admin',
    'Client ID': 'CLI-001',
    'Language': 'en',
    'Theme': 'snow',
    'Is Active': True
}]

phases_data = [
    {'ID': 'PHS-001', 'Name': 'Planning', 'Short Description': 'Planning phase', 'Long Description': 'Initial planning and requirements gathering', 'Color': '#3B82F6', 'Display Order': 1, 'Is Active': True},
    {'ID': 'PHS-002', 'Name': 'Design', 'Short Description': 'Design phase', 'Long Description': 'System and UI/UX design', 'Color': '#8B5CF6', 'Display Order': 2, 'Is Active': True},
    {'ID': 'PHS-003', 'Name': 'Development', 'Short Description': 'Development phase', 'Long Description': 'Implementation and coding', 'Color': '#10B981', 'Display Order': 3, 'Is Active': True},
    {'ID': 'PHS-004', 'Name': 'Testing', 'Short Description': 'Testing phase', 'Long Description': 'Quality assurance and testing', 'Color': '#F59E0B', 'Display Order': 4, 'Is Active': True},
    {'ID': 'PHS-005', 'Name': 'Deployment', 'Short Description': 'Deployment phase', 'Long Description': 'Production deployment', 'Color': '#EF4444', 'Display Order': 5, 'Is Active': True}
]

programs_data = [{
    'ID': 'PRG-001',
    'Client ID': 'CLI-001',
    'Name': 'Digital Transformation',
    'Short Description': 'Company-wide digital transformation initiative',
    'Long Description': 'Comprehensive digital transformation program to modernize all business processes.',
    'Status': 'Active',
    'Start Date': '2025-01-01',
    'End Date': '2025-12-31'
}]

projects_data = [{
    'ID': 'PRJ-001',
    'Program ID': 'PRG-001',
    'Name': 'Worky Platform',
    'Short Description': 'Project management platform',
    'Long Description': 'Development of comprehensive project management and tracking platform.',
    'Status': 'Active',
    'Start Date': '2025-01-01',
    'End Date': '2025-06-30',
    'Repository URL': 'https://github.com/company/worky'
}]

usecases_data = [{
    'ID': 'UC-001',
    'Project ID': 'PRJ-001',
    'Name': 'User Management',
    'Short Description': 'Manage users and permissions',
    'Long Description': 'Complete user management system with role-based access control.',
    'Priority': 'High',
    'Status': 'In Progress'
}]

user_stories_data = [{
    'ID': 'US-001',
    'Use Case ID': 'UC-001',
    'Name': 'User Login',
    'Short Description': 'Users can log in to the system',
    'Long Description': 'As a user, I want to log in to the system so that I can access my workspace.',
    'Acceptance Criteria': 'User can enter email and password and successfully authenticate',
    'Priority': 'High',
    'Status': 'In Progress',
    'Story Points': 5
}]

tasks_data = [{
    'ID': 'TSK-001',
    'User Story ID': 'US-001',
    'Phase ID': 'PHS-003',
    'Name': 'Implement login API',
    'Short Description': 'Create login endpoint',
    'Long Description': 'Implement FastAPI endpoint for user authentication with JWT tokens.',
    'Status': 'In Progress',
    'Priority': 'High',
    'Assigned To': 'USR-001',
    'Estimated Hours': 8,
    'Actual Hours': 6,
    'Start Date': '2025-01-15',
    'Due Date': '2025-01-20'
}]

subtasks_data = [{
    'ID': 'ST-001',
    'Task ID': 'TSK-001',
    'Phase ID': 'PHS-003',
    'Name': 'Create authentication service',
    'Short Description': 'Build auth service',
    'Long Description': 'Create authentication service with password hashing and JWT generation.',
    'Status': 'Completed',
    'Assigned To': 'USR-001',
    'Estimated Hours': 4,
    'Actual Hours': 3
}]

bugs_data = [{
    'ID': 'BUG-001',
    'Entity Type': 'Task',
    'Entity ID': 'TSK-001',
    'Title': 'Login fails with special characters',
    'Short Description': 'Password validation issue',
    'Long Description': 'Login fails when password contains special characters like @ or #.',
    'Severity': 'High',
    'Priority': 'P0',
    'Status': 'New',
    'Reported By': 'USR-001',
    'Assigned To': 'USR-001',
    'Resolution Notes': ''
}]

def save_data():
    """Save all sample data to Excel files"""
    print("Creating sample data in Excel files...")
    print()
    
    data_map = {
        'clients.xlsx': clients_data,
        'users.xlsx': users_data,
        'phases.xlsx': phases_data,
        'programs.xlsx': programs_data,
        'projects.xlsx': projects_data,
        'usecases.xlsx': usecases_data,
        'user_stories.xlsx': user_stories_data,
        'tasks.xlsx': tasks_data,
        'subtasks.xlsx': subtasks_data,
        'bugs.xlsx': bugs_data
    }
    
    for filename, data in data_map.items():
        filepath = os.path.join(EXCEL_DIR, filename)
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        print(f"✓ Created {filename} with {len(data)} rows")
    
    print()
    print("=" * 60)
    print("Sample data created successfully!")
    print("Run: python3 load_data.py")
    print("=" * 60)

if __name__ == '__main__':
    save_data()

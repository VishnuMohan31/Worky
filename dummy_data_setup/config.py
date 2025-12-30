"""
Database configuration for dummy data loader
All parameters loaded from environment variables or .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration - all from environment variables
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', '5437')),
    'database': os.getenv('DATABASE_NAME', 'worky'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', 'postgres')
}

# Excel templates directory
EXCEL_DIR = os.path.join(os.path.dirname(__file__), 'excel_templates')

# Table loading order (respects foreign key dependencies)
LOAD_ORDER = [
    'clients',
    'users',
    'phases',
    'programs',
    'projects',
    'usecases',
    'user_stories',
    'tasks',
    'subtasks',
    'bugs'
]

# Table to Excel file mapping
TABLE_FILES = {
    'users': 'users.xlsx',
    'clients': 'clients.xlsx',
    'programs': 'programs.xlsx',
    'projects': 'projects.xlsx',
    'phases': 'phases.xlsx',
    'usecases': 'usecases.xlsx',
    'user_stories': 'user_stories.xlsx',
    'tasks': 'tasks.xlsx',
    'subtasks': 'subtasks.xlsx',
    'bugs': 'bugs.xlsx'
}

# Column mappings (Excel column name -> Database column name)
COLUMN_MAPPINGS = {
    'clients': {
        'ID': 'id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Is Active': 'is_active'
    },
    'programs': {
        'ID': 'id',
        'Client ID': 'client_id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Status': 'status',
        'Start Date': 'start_date',
        'End Date': 'end_date'
    },
    'projects': {
        'ID': 'id',
        'Program ID': 'program_id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Status': 'status',
        'Start Date': 'start_date',
        'End Date': 'end_date',
        'Repository URL': 'repository_url'
    },
    'usecases': {
        'ID': 'id',
        'Project ID': 'project_id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Priority': 'priority',
        'Status': 'status'
    },
    'user_stories': {
        'ID': 'id',
        'Use Case ID': 'usecase_id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Acceptance Criteria': 'acceptance_criteria',
        'Priority': 'priority',
        'Status': 'status',
        'Story Points': 'story_points'
    },
    'tasks': {
        'ID': 'id',
        'User Story ID': 'user_story_id',
        'Phase ID': 'phase_id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Status': 'status',
        'Priority': 'priority',
        'Assigned To': 'assigned_to',
        'Estimated Hours': 'estimated_hours',
        'Actual Hours': 'actual_hours',
        'Start Date': 'start_date',
        'Due Date': 'due_date'
    },
    'subtasks': {
        'ID': 'id',
        'Task ID': 'task_id',
        'Phase ID': 'phase_id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Status': 'status',
        'Assigned To': 'assigned_to',
        'Estimated Hours': 'estimated_hours',
        'Actual Hours': 'actual_hours'
    },
    'bugs': {
        'ID': 'id',
        'Entity Type': 'entity_type',
        'Entity ID': 'entity_id',
        'Title': 'title',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Severity': 'severity',
        'Priority': 'priority',
        'Status': 'status',
        'Reported By': 'reported_by',
        'Assigned To': 'assigned_to',
        'Resolution Notes': 'resolution_notes'
    },
    'users': {
        'ID': 'id',
        'Email': 'email',
        'Password': 'password',
        'Full Name': 'full_name',
        'Role': 'role',
        'Client ID': 'client_id',
        'Language': 'language',
        'Theme': 'theme',
        'Is Active': 'is_active'
    },
    'phases': {
        'ID': 'id',
        'Name': 'name',
        'Short Description': 'short_description',
        'Long Description': 'long_description',
        'Color': 'color',
        'Display Order': 'display_order',
        'Is Active': 'is_active'
    }
}

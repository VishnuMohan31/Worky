#!/usr/bin/env python3
"""
Load project data from Google Sheets into Worky database
"""

import os
import sys
import gspread
from google.oauth2.service_account import Credentials
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': os.getenv('DATABASE_PORT', '5437'),
    'database': os.getenv('DATABASE_NAME', 'worky'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', 'postgres')
}

# Google Sheets configuration
SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '1bWsGB83O6GFZf2pRmm485it2X_XN1Rh8eCFs8knjHS0')
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')

# Define the scope
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]


class SheetsDataLoader:
    def __init__(self):
        self.conn = None
        self.gc = None
        self.spreadsheet = None
        
    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            print(f"✓ Connected to database: {DB_CONFIG['database']}")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def connect_to_sheets(self):
        """Connect to Google Sheets"""
        try:
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                print(f"✗ Service account file not found: {SERVICE_ACCOUNT_FILE}")
                print("  Please download your service account JSON from Google Cloud Console")
                return False
            
            creds = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=SCOPES
            )
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_key(SHEETS_ID)
            print(f"✓ Connected to Google Sheets: {self.spreadsheet.title}")
            return True
        except Exception as e:
            print(f"✗ Google Sheets connection failed: {e}")
            return False
    
    def get_sheet_data(self, sheet_name):
        """Get data from a specific sheet"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            data = worksheet.get_all_records()
            print(f"✓ Loaded {len(data)} rows from sheet: {sheet_name}")
            return data
        except Exception as e:
            print(f"✗ Failed to load sheet '{sheet_name}': {e}")
            return []
    
    def load_clients(self, sheet_name='Clients'):
        """Load clients from sheet"""
        data = self.get_sheet_data(sheet_name)
        if not data:
            return
        
        cursor = self.conn.cursor()
        inserted = 0
        
        for row in data:
            try:
                # Extract relevant fields
                name = row.get('Client Name') or row.get('Name') or row.get('client_name')
                description = row.get('Description') or row.get('description', '')
                is_active = row.get('Active', 'Yes').lower() in ['yes', 'true', '1', 'active']
                
                if not name:
                    continue
                
                # Insert client
                cursor.execute("""
                    INSERT INTO clients (name, description, is_active)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (name, description, is_active))
                
                if cursor.fetchone():
                    inserted += 1
                    
            except Exception as e:
                print(f"  Warning: Failed to insert client '{name}': {e}")
                continue
        
        self.conn.commit()
        print(f"✓ Inserted {inserted} clients")
    
    def load_users(self, sheet_name='Users'):
        """Load users from sheet"""
        data = self.get_sheet_data(sheet_name)
        if not data:
            return
        
        cursor = self.conn.cursor()
        inserted = 0
        
        # Get first client ID as default
        cursor.execute("SELECT id FROM clients LIMIT 1")
        default_client_id = cursor.fetchone()[0]
        
        for row in data:
            try:
                email = row.get('Email') or row.get('email')
                full_name = row.get('Full Name') or row.get('Name') or row.get('full_name')
                role = row.get('Role') or row.get('role', 'Developer')
                
                if not email or not full_name:
                    continue
                
                # Default password hash for 'password'
                hashed_password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.xKfvGK'
                
                cursor.execute("""
                    INSERT INTO users (email, hashed_password, full_name, role, client_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                """, (email, hashed_password, full_name, role, default_client_id))
                
                if cursor.fetchone():
                    inserted += 1
                    
            except Exception as e:
                print(f"  Warning: Failed to insert user '{email}': {e}")
                continue
        
        self.conn.commit()
        print(f"✓ Inserted {inserted} users")
    
    def load_projects(self, sheet_name='Projects'):
        """Load projects from sheet"""
        data = self.get_sheet_data(sheet_name)
        if not data:
            return
        
        cursor = self.conn.cursor()
        inserted = 0
        
        # Get first program ID as default
        cursor.execute("SELECT id FROM programs LIMIT 1")
        result = cursor.fetchone()
        if not result:
            # Create a default program
            cursor.execute("SELECT id FROM clients LIMIT 1")
            client_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO programs (client_id, name, description)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (client_id, 'Default Program', 'Auto-created program'))
            result = cursor.fetchone()
        
        default_program_id = result[0]
        
        for row in data:
            try:
                name = row.get('Project Name') or row.get('Name') or row.get('project_name')
                description = row.get('Description') or row.get('description', '')
                status = row.get('Status') or row.get('status', 'Planning')
                start_date = row.get('Start Date') or row.get('start_date')
                end_date = row.get('End Date') or row.get('end_date')
                
                if not name:
                    continue
                
                cursor.execute("""
                    INSERT INTO projects (program_id, name, description, status, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (default_program_id, name, description, status, start_date, end_date))
                
                if cursor.fetchone():
                    inserted += 1
                    
            except Exception as e:
                print(f"  Warning: Failed to insert project '{name}': {e}")
                continue
        
        self.conn.commit()
        print(f"✓ Inserted {inserted} projects")
    
    def load_tasks(self, sheet_name='Tasks'):
        """Load tasks from sheet"""
        data = self.get_sheet_data(sheet_name)
        if not data:
            return
        
        cursor = self.conn.cursor()
        inserted = 0
        
        # Get first user story ID as default
        cursor.execute("""
            SELECT us.id 
            FROM user_stories us 
            JOIN usecases uc ON us.usecase_id = uc.id 
            JOIN projects p ON uc.project_id = p.id 
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if not result:
            # Create default hierarchy
            cursor.execute("SELECT id FROM projects LIMIT 1")
            project_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO usecases (project_id, name, description)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (project_id, 'Default Usecase', 'Auto-created usecase'))
            usecase_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO user_stories (usecase_id, title, description)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (usecase_id, 'Default User Story', 'Auto-created user story'))
            result = cursor.fetchone()
        
        default_user_story_id = result[0]
        
        for row in data:
            try:
                title = row.get('Task Name') or row.get('Title') or row.get('task_name')
                description = row.get('Description') or row.get('description', '')
                status = row.get('Status') or row.get('status', 'To Do')
                priority = row.get('Priority') or row.get('priority', 'Medium')
                assigned_to_email = row.get('Assigned To') or row.get('assigned_to')
                due_date = row.get('Due Date') or row.get('due_date')
                
                if not title:
                    continue
                
                # Get assigned user ID if email provided
                assigned_to = None
                if assigned_to_email:
                    cursor.execute("SELECT id FROM users WHERE email = %s", (assigned_to_email,))
                    user_result = cursor.fetchone()
                    if user_result:
                        assigned_to = user_result[0]
                
                cursor.execute("""
                    INSERT INTO tasks (user_story_id, title, description, status, priority, assigned_to, due_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (default_user_story_id, title, description, status, priority, assigned_to, due_date))
                
                if cursor.fetchone():
                    inserted += 1
                    
            except Exception as e:
                print(f"  Warning: Failed to insert task '{title}': {e}")
                continue
        
        self.conn.commit()
        print(f"✓ Inserted {inserted} tasks")
    
    def list_available_sheets(self):
        """List all available sheets in the spreadsheet"""
        if not self.spreadsheet:
            return []
        
        worksheets = self.spreadsheet.worksheets()
        print("\n📋 Available sheets:")
        for ws in worksheets:
            print(f"  - {ws.title} ({ws.row_count} rows, {ws.col_count} columns)")
        return [ws.title for ws in worksheets]
    
    def load_all(self):
        """Load all data from sheets"""
        print("\n🔄 Loading data from Google Sheets...")
        
        # List available sheets
        available_sheets = self.list_available_sheets()
        
        # Try to load common sheet names
        sheet_mappings = {
            'Clients': ['Clients', 'Client', 'clients', 'client'],
            'Users': ['Users', 'User', 'Team', 'People', 'users', 'team'],
            'Projects': ['Projects', 'Project', 'projects', 'project'],
            'Tasks': ['Tasks', 'Task', 'Work Items', 'tasks', 'task']
        }
        
        for data_type, possible_names in sheet_mappings.items():
            found = False
            for name in possible_names:
                if name in available_sheets:
                    print(f"\n📊 Loading {data_type} from sheet: {name}")
                    if data_type == 'Clients':
                        self.load_clients(name)
                    elif data_type == 'Users':
                        self.load_users(name)
                    elif data_type == 'Projects':
                        self.load_projects(name)
                    elif data_type == 'Tasks':
                        self.load_tasks(name)
                    found = True
                    break
            
            if not found:
                print(f"⚠️  No sheet found for {data_type}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\n✓ Database connection closed")


def main():
    print("=" * 60)
    print("Worky Data Loader - Google Sheets to Database")
    print("=" * 60)
    
    loader = SheetsDataLoader()
    
    # Connect to database
    if not loader.connect_to_database():
        sys.exit(1)
    
    # Connect to Google Sheets
    if not loader.connect_to_sheets():
        print("\n💡 Setup Instructions:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Sheets API and Google Drive API")
        print("4. Create a Service Account")
        print("5. Download the JSON key file")
        print("6. Save it as 'service_account.json' in this directory")
        print("7. Share your Google Sheet with the service account email")
        sys.exit(1)
    
    # Load all data
    try:
        loader.load_all()
        print("\n" + "=" * 60)
        print("✅ Data loading complete!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error during data loading: {e}")
        sys.exit(1)
    finally:
        loader.close()


if __name__ == "__main__":
    main()

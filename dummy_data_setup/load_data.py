"""
Load dummy data from Excel files into PostgreSQL database
"""
import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import bcrypt
from config import DB_CONFIG, EXCEL_DIR, LOAD_ORDER, TABLE_FILES, COLUMN_MAPPINGS

def hash_password(password):
    """Hash password using bcrypt"""
    if not password or pd.isna(password):
        password = 'password123'
    pwd_bytes = str(password).encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def load_excel_file(filepath):
    """Load data from Excel file"""
    try:
        df = pd.read_excel(filepath)
        return df
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading Excel file {filepath}: {e}")
        return None

def map_columns(df, table_name):
    """Map Excel columns to database columns"""
    if table_name not in COLUMN_MAPPINGS:
        return df
    
    mapping = COLUMN_MAPPINGS[table_name]
    df_mapped = df.rename(columns=mapping)
    
    # Keep only mapped columns
    valid_columns = list(mapping.values())
    df_mapped = df_mapped[[col for col in valid_columns if col in df_mapped.columns]]
    
    return df_mapped

def insert_data(conn, table_name, df):
    """Insert data into database table"""
    if df is None or df.empty:
        print(f"  No data to insert for {table_name}")
        return 0
    
    cursor = conn.cursor()
    
    # Replace NaN with None for SQL NULL
    df = df.where(pd.notnull(df), None)
    
    # Special handling for users table - hash passwords
    if table_name == 'users' and 'password' in df.columns:
        df['hashed_password'] = df['password'].apply(hash_password)
        df = df.drop(columns=['password'])
    
    # Get column names and values
    columns = df.columns.tolist()
    values = df.values.tolist()
    
    # Build INSERT query
    cols_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"
    
    try:
        cursor.executemany(query, values)
        conn.commit()
        inserted = cursor.rowcount
        print(f"  ✓ Inserted {inserted} rows into {table_name}")
        return inserted
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error inserting into {table_name}: {e}")
        return 0
    finally:
        cursor.close()

def clear_table(conn, table_name):
    """Clear all data from a table"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        conn.commit()
        print(f"  Cleared table {table_name}")
    except Exception as e:
        conn.rollback()
        print(f"  Warning: Could not clear {table_name}: {e}")
    finally:
        cursor.close()

def main():
    """Main execution"""
    print("=" * 60)
    print("Worky Dummy Data Loader")
    print("=" * 60)
    print()
    
    # Check if excel_templates directory exists
    if not os.path.exists(EXCEL_DIR):
        print(f"Error: Excel templates directory not found: {EXCEL_DIR}")
        print("Please create the directory and add Excel files.")
        sys.exit(1)
    
    # Connect to database
    print("Connecting to database...")
    print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    conn = get_db_connection()
    print("  ✓ Connected successfully")
    print()
    
    # Ask if user wants to clear existing data
    response = input("Clear existing data before loading? (y/N): ").strip().lower()
    clear_data = response == 'y'
    print()
    
    if clear_data:
        print("Clearing existing data...")
        for table in reversed(LOAD_ORDER):
            clear_table(conn, table)
        print()
    
    # Load data for each table
    print("Loading data from Excel files...")
    print()
    
    total_inserted = 0
    for table in LOAD_ORDER:
        print(f"Processing {table}...")
        
        # Get Excel file path
        excel_file = TABLE_FILES.get(table)
        if not excel_file:
            print(f"  Warning: No Excel file configured for {table}")
            continue
        
        filepath = os.path.join(EXCEL_DIR, excel_file)
        
        # Load Excel data
        df = load_excel_file(filepath)
        if df is None:
            continue
        
        print(f"  Loaded {len(df)} rows from Excel")
        
        # Map columns
        df_mapped = map_columns(df, table)
        
        # Insert data
        inserted = insert_data(conn, table, df_mapped)
        total_inserted += inserted
        print()
    
    # Close connection
    conn.close()
    
    print("=" * 60)
    print(f"Data loading complete!")
    print(f"Total rows inserted: {total_inserted}")
    print("=" * 60)

if __name__ == '__main__':
    main()

"""
Create Excel template files with proper column headers
"""
import os
import pandas as pd
from config import EXCEL_DIR, COLUMN_MAPPINGS

def create_template(table_name, columns):
    """Create an Excel template with column headers"""
    # Create DataFrame with column headers
    df = pd.DataFrame(columns=columns)
    
    # Add sample row with data types as hints
    sample_row = {}
    for col in columns:
        if 'ID' in col or 'id' in col.lower():
            sample_row[col] = 'string-id'
        elif 'Date' in col or 'date' in col.lower():
            sample_row[col] = '2025-01-01'
        elif 'Email' in col or 'email' in col.lower():
            sample_row[col] = 'user@example.com'
        elif 'Phone' in col or 'phone' in col.lower():
            sample_row[col] = '+1-555-0100'
        elif 'Is Active' in col or 'is_active' in col.lower():
            sample_row[col] = 'TRUE'
        elif 'Status' in col:
            sample_row[col] = 'Active'
        elif 'Priority' in col:
            sample_row[col] = 'High'
        elif 'Severity' in col:
            sample_row[col] = 'Medium'
        elif 'Role' in col:
            sample_row[col] = 'Admin'
        elif 'Points' in col:
            sample_row[col] = 5
        else:
            sample_row[col] = 'Sample text'
    
    df = pd.concat([df, pd.DataFrame([sample_row])], ignore_index=True)
    
    return df

def main():
    """Generate all Excel templates"""
    print("Creating Excel templates...")
    print()
    
    # Create excel_templates directory if it doesn't exist
    os.makedirs(EXCEL_DIR, exist_ok=True)
    
    for table_name, mapping in COLUMN_MAPPINGS.items():
        # Get Excel column names
        excel_columns = list(mapping.keys())
        
        # Create template
        df = create_template(table_name, excel_columns)
        
        # Save to Excel
        filename = f"{table_name}.xlsx"
        filepath = os.path.join(EXCEL_DIR, filename)
        df.to_excel(filepath, index=False)
        
        print(f"✓ Created {filename} with {len(excel_columns)} columns")
    
    print()
    print("=" * 60)
    print("Excel templates created successfully!")
    print(f"Location: {EXCEL_DIR}")
    print()
    print("Next steps:")
    print("1. Open each Excel file")
    print("2. Delete the sample row")
    print("3. Add your dummy data")
    print("4. Run: python load_data.py")
    print("=" * 60)

if __name__ == '__main__':
    main()

# Dummy Data Setup

This directory contains scripts and Excel templates for loading dummy data into the Worky database.

## Structure

- `excel_templates/` - Excel sheet templates for each table
- `load_data.py` - Main script to load data from Excel to database
- `requirements.txt` - Python dependencies
- `config.py` - Database configuration

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Fill in the Excel templates in `excel_templates/` directory

3. Update database configuration in `config.py` or use environment variables

4. Run the loader:
```bash
python load_data.py
```

## Excel Templates

Each Excel file corresponds to a database table:
- `clients.xlsx` - Client data
- `programs.xlsx` - Program data
- `projects.xlsx` - Project data
- `usecases.xlsx` - Use case data
- `user_stories.xlsx` - User story data
- `tasks.xlsx` - Task data
- `subtasks.xlsx` - Subtask data
- `bugs.xlsx` - Bug data
- `users.xlsx` - User data
- `phases.xlsx` - Phase data

## Column Mapping

Each Excel sheet should have columns matching the database table structure.
See individual template files for required columns.

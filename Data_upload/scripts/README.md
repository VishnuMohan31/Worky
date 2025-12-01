# Data Upload Scripts

This directory contains scripts for loading data into the Worky database.

## Excel Data Loader

The Excel Data Loader is a FastAPI-based service that enables bulk-importing of project tracking data from Excel files into the Worky database.

### Prerequisites

- **Python 3.9+** - Check version: `python3 --version`
- **PostgreSQL Access** - Worky database must be running and accessible
- **Excel File** - .xlsx or .xls format with required sheets (Projects, Usecases, Userstories, Tasks, Subtasks)

### Quick Start

1. **Install dependencies:**
   ```bash
   cd excel_loader
   pip install -r requirements.txt
   ```

2. **Configure database connection:**
   ```bash
   cd excel_loader
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Start the loader service:**
   ```bash
   ./start_loader.sh
   ```
   
   The service will start on `http://localhost:8001`

4. **Import an Excel file:**
   ```bash
   curl -X POST http://localhost:8001/api/import \
     -F "file=@../data/Project Tracking Automation.xlsx"
   ```

### Documentation

For complete documentation, see [excel_loader/README.md](excel_loader/README.md)

The detailed README includes:
- Prerequisites and installation instructions
- Environment variable configuration
- Multiple ways to run the service
- API usage examples (curl, Python)
- Expected Excel file structure with examples
- Comprehensive troubleshooting guide
- Example responses for success and error cases
- Architecture overview

### Directory Structure

```
Data_upload/scripts/
├── README.md                    # This file
├── start_loader.sh             # Startup script for the loader service
└── excel_loader/               # Excel loader application
    ├── README.md               # Detailed documentation
    ├── requirements.txt        # Python dependencies
    ├── .env.example           # Environment configuration template
    ├── excel_loader_app.py    # FastAPI application
    ├── import_orchestrator.py # Import coordination
    ├── excel_parser.py        # Excel file parsing
    ├── data_mapper.py         # Column mapping and conversion
    ├── hierarchy_builder.py   # Relationship management
    ├── database_writer.py     # Database operations
    ├── models.py              # Data models
    └── db_utils.py            # Database utilities
```

### Features

- **Hierarchical Import**: Maintains parent-child relationships (Clients → Programs → Projects → Usecases → User Stories → Tasks → Subtasks)
- **Intelligent Mapping**: Automatically maps Excel columns to database fields
- **Default Values**: Fills missing required fields with appropriate defaults
- **Type Conversion**: Handles dates, numbers, percentages automatically
- **User Resolution**: Matches user names/emails to existing database users
- **Transaction Safety**: All-or-nothing imports with automatic rollback on errors
- **Error Handling**: Comprehensive error messages and warnings
- **Progress Tracking**: Detailed logging and import summaries

### Requirements

- Python 3.9+
- PostgreSQL database (Worky)
- Excel file (.xlsx or .xls format)

### Support

For issues or questions:
1. Check the [detailed README](excel_loader/README.md)
2. Review the troubleshooting section
3. Verify your Excel file structure
4. Check the service logs

### Example Excel File

An example Excel file is provided at:
```
Data_upload/data/Project Tracking Automation.xlsx
```

This file demonstrates the expected structure with sample data.

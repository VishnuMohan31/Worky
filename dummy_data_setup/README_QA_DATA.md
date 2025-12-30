# QA Dummy Data Generation

This directory contains scripts for generating and loading realistic QA testing data including test runs, test cases, and bugs.

## Overview

The QA data generation follows the QA Testing and Bug Management specification and creates:
- **20 test runs** distributed across hierarchy levels (Project → Subtask)
- **50 test cases** linked to test runs with realistic execution statuses
- **60 bugs** (40 from failed test cases, 20 created directly at hierarchy levels)
- **130+ comments** on bugs and test cases
- **Bug status history** showing realistic lifecycle transitions
- **Bug assignments** tracking who is assigned to fix each bug

## Files

### Scripts

- **`create_qa_templates.py`** - Creates Excel templates with sample data and instructions
- **`create_qa_data.py`** - Generates realistic QA dummy data programmatically
- **`load_qa_data.py`** - Loads generated data into the database via API endpoints

### Excel Templates (in `excel_templates/`)

- **`test_runs.xlsx`** - Test run definitions with hierarchy associations
- **`test_cases.xlsx`** - Test cases linked to test runs
- **`bugs_extended.xlsx`** - Bugs with full QA fields (category, severity, priority, etc.)
- **`comments.xlsx`** - Comments on bugs and test cases
- **`bug_status_history.xlsx`** - Bug status transition history
- **`bug_assignments.xlsx`** - Bug assignment records

## Usage

### Step 1: Create Excel Templates (Optional)

If you want to manually edit the templates before generating data:

```bash
python3 create_qa_templates.py
```

This creates template files with:
- Sample data rows showing the correct format
- Instructions row explaining each field
- Proper column headers

### Step 2: Generate Dummy Data

Generate realistic QA data programmatically:

```bash
python3 create_qa_data.py
```

This will:
- Generate 20 test runs across all hierarchy levels
- Generate 50 test cases with realistic statuses (Passed, Failed, Blocked, etc.)
- Generate 60 bugs with varied categories, severities, and priorities
- Generate 130+ comments with @mentions
- Generate bug status history showing lifecycle transitions
- Generate bug assignments

**Output:**
- Excel files in `excel_templates/` directory
- Summary statistics printed to console

### Step 3: Load Data via API

Load the generated data into the database using real API endpoints:

```bash
python3 load_qa_data.py
```

**Prerequisites:**
- API server must be running (default: http://localhost:8007)
- Valid user credentials in `.env` file
- Database must be initialized with migrations

**Environment Variables:**
```bash
API_BASE_URL=http://localhost:8007/api/v1
API_USER_EMAIL=admin@datalegos.com
API_USER_PASSWORD=password
```

The script will:
1. Authenticate with the API
2. Create test runs
3. Create test cases linked to test runs
4. Create bugs (linked to test cases or hierarchy)
5. Create comments on bugs and test cases
6. Apply bug status transitions
7. Apply bug assignments

## Data Distribution

### Test Runs (20 total)
- 5 at Project level
- 5 at Use Case level
- 4 at User Story level
- 4 at Task level
- 2 at Subtask level

### Test Cases (50 total)
Distributed across test runs with realistic statuses:
- ~54% Passed
- ~16% Failed
- ~12% Not Executed
- ~10% Blocked
- ~8% Skipped

### Bugs (60 total)
- **40 bugs from test cases** - Created from failed test executions
  - Linked to test_run_id and test_case_id
  - Pre-populated with test case details
- **20 direct bugs** - Created at hierarchy levels
  - Linked to Project, Use Case, User Story, Task, or Subtask
  - Manual reproduction steps

**Status Distribution:**
- New, Open, In Progress: ~50%
- Fixed, Ready for Testing: ~20%
- Verified, Closed: ~25%
- Reopened, Deferred: ~5%

**Severity Distribution:**
- Critical/Blocker: ~25%
- Major: ~25%
- Minor: ~30%
- Trivial: ~20%

### Comments (130+ total)
- 100 bug comments with @mentions
- 30 test case comments
- Realistic timestamps spread over 90 days

### Bug Status History (150+ entries)
- Tracks all status transitions
- Includes resolution notes
- Shows realistic bug lifecycle

## Customization

### Modify Data Quantities

Edit `create_qa_data.py` and change the counts in `save_qa_data()`:

```python
test_runs = generate_test_runs(20)      # Change to desired count
test_cases = generate_test_cases(test_runs, 50)  # Change to desired count
bugs = generate_bugs(test_cases, 60)    # Change to desired count
```

### Modify Data Distributions

Edit the distribution arrays in the generation functions:

```python
# In generate_test_runs()
hierarchy_distribution = (
    [('project', PROJECTS[0])] * 5 +    # Adjust counts
    [('usecase', USECASES[0])] * 5 +
    # ...
)

# In generate_test_cases()
status = random.choice(['Passed'] * 6 + ['Failed'] * 2 + ...)  # Adjust weights
```

### Add More Reference Data

Edit the constants at the top of `create_qa_data.py`:

```python
PROJECTS = ['PRJ-001', 'PRJ-002']  # Add more projects
USECASES = ['UC-001', 'UC-002']    # Add more use cases
USERS = ['USR-001', 'USR-002']     # Add more users
```

## Data Validation

After loading, verify the data:

```bash
# Check test runs
curl http://localhost:8007/api/v1/test-runs/

# Check test cases
curl http://localhost:8007/api/v1/test-cases/

# Check bugs
curl http://localhost:8007/api/v1/bugs/hierarchy

# Check bug metrics
curl http://localhost:8007/api/v1/qa-metrics/bugs/summary
```

## Troubleshooting

### Authentication Fails
- Verify API server is running
- Check credentials in `.env` file
- Ensure user exists in database

### API Endpoints Not Found
- Verify all QA endpoints are implemented
- Check API version in URL
- Review API logs for errors

### Data Not Appearing
- Check for validation errors in API response
- Verify foreign key references exist
- Review database constraints

### Excel File Errors
- Ensure pandas and openpyxl are installed: `pip install pandas openpyxl`
- Check file permissions in `excel_templates/` directory

## Requirements

```bash
pip install pandas openpyxl requests python-dotenv
```

## Notes

- The script uses `random.seed(42)` for reproducibility
- All dates are relative to current date (past 90 days)
- Bug ages are varied to test aging reports
- Test case execution dates are within test run date ranges
- Comments have realistic timestamps
- Status history shows proper lifecycle transitions

## Next Steps

After loading the data:
1. Review the data in the UI
2. Test the QA workflows (test execution, bug creation)
3. Verify metrics and reports
4. Test hierarchical bug viewing
5. Test bug lifecycle transitions

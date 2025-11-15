# 📊 Worky Data Loader - Google Sheets Integration

Load project data from Google Sheets into your Worky database.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd db/db_loader
pip install -r requirements.txt
```

### 2. Set Up Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Google Sheets API
   - Google Drive API
4. Create a Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "worky-sheets-loader")
   - Click "Create and Continue"
   - Skip role assignment (click "Continue")
   - Click "Done"
5. Create a key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON"
   - Download the file
6. Save the downloaded JSON file as `service_account.json` in this directory

### 3. Share Your Google Sheet

1. Open your Google Sheet
2. Click "Share" button
3. Add the service account email (found in the JSON file, looks like: `worky-sheets-loader@project-id.iam.gserviceaccount.com`)
4. Give it "Viewer" access
5. Click "Send"

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

Default `.env`:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5437
DATABASE_NAME=worky
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

GOOGLE_SHEETS_ID=1bWsGB83O6GFZf2pRmm485it2X_XN1Rh8eCFs8knjHS0
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
```

### 5. Run the Loader

```bash
python load_from_sheets.py
```

## 📋 Expected Sheet Structure

The loader will look for sheets with these names (case-insensitive):

### Clients Sheet
| Column | Description | Required |
|--------|-------------|----------|
| Client Name / Name | Client organization name | Yes |
| Description | Client description | No |
| Active | Yes/No or True/False | No |

### Users Sheet
| Column | Description | Required |
|--------|-------------|----------|
| Email | User email address | Yes |
| Full Name / Name | User's full name | Yes |
| Role | User role (Admin, Developer, etc.) | No |

### Projects Sheet
| Column | Description | Required |
|--------|-------------|----------|
| Project Name / Name | Project name | Yes |
| Description | Project description | No |
| Status | Planning, In Progress, etc. | No |
| Start Date | Project start date | No |
| End Date | Project end date | No |

### Tasks Sheet
| Column | Description | Required |
|--------|-------------|----------|
| Task Name / Title | Task title | Yes |
| Description | Task description | No |
| Status | To Do, In Progress, Done | No |
| Priority | High, Medium, Low | No |
| Assigned To | User email | No |
| Due Date | Task due date | No |

## 🔧 How It Works

1. **Connects to Database**: Uses PostgreSQL connection on port 5437
2. **Connects to Google Sheets**: Uses service account authentication
3. **Lists Available Sheets**: Shows all sheets in the spreadsheet
4. **Loads Data**: Processes each sheet and inserts into database
5. **Handles Conflicts**: Skips duplicates, creates default hierarchies

## 📊 Data Mapping

The loader intelligently maps sheet data to database tables:

- **Clients** → `clients` table
- **Users** → `users` table (with default password: "password")
- **Projects** → `projects` table (creates default program if needed)
- **Tasks** → `tasks` table (creates default usecase/story if needed)

## ⚠️ Important Notes

1. **Default Password**: All loaded users get password: `password`
2. **Default Hierarchy**: If projects/tasks don't have parent entities, defaults are created
3. **Duplicate Handling**: Existing records are skipped (no updates)
4. **Email Matching**: Task assignments use email to find users

## 🐛 Troubleshooting

### "Service account file not found"
- Make sure `service_account.json` is in the `db/db_loader/` directory
- Check the filename matches exactly

### "Permission denied" or "Requested entity was not found"
- Make sure you shared the Google Sheet with the service account email
- Check the GOOGLE_SHEETS_ID in .env is correct

### "Database connection failed"
- Make sure PostgreSQL is running: `docker-compose ps`
- Check database credentials in .env
- Verify port 5437 is correct

### "No sheet found for [type]"
- Check your sheet names match expected names
- Sheet names are case-sensitive
- You can rename sheets in Google Sheets to match

## 📝 Example Google Sheet Structure

**Sheet: Clients**
```
Client Name    | Description              | Active
DataLegos      | Internal projects        | Yes
Acme Corp      | Manufacturing client     | Yes
```

**Sheet: Users**
```
Email                  | Full Name      | Role
john@datalegos.com     | John Doe       | Developer
jane@datalegos.com     | Jane Smith     | Project Manager
```

**Sheet: Projects**
```
Project Name     | Description                    | Status       | Start Date  | End Date
Worky Platform   | Project management system      | In Progress  | 2025-01-01  | 2025-06-30
Customer Portal  | Self-service portal            | Planning     | 2025-02-01  | 2025-08-31
```

**Sheet: Tasks**
```
Task Name              | Description                  | Status       | Priority | Assigned To           | Due Date
Design database        | Create PostgreSQL schema     | Done         | High     | john@datalegos.com    | 2025-01-15
Implement auth         | JWT authentication           | In Progress  | High     | john@datalegos.com    | 2025-01-20
```

## 🔄 Re-running the Loader

You can run the loader multiple times:
- Existing records are skipped (based on unique constraints)
- New records are added
- No data is updated or deleted

## 🎯 Advanced Usage

### Load Specific Sheets Only

Edit `load_from_sheets.py` and comment out unwanted loaders:

```python
# loader.load_clients('Clients')
loader.load_users('Users')
loader.load_projects('Projects')
# loader.load_tasks('Tasks')
```

### Custom Sheet Names

If your sheets have different names, update the `sheet_mappings` in `load_from_sheets.py`:

```python
sheet_mappings = {
    'Clients': ['My Clients Sheet'],
    'Users': ['Team Members'],
    'Projects': ['Active Projects'],
    'Tasks': ['Work Items']
}
```

## 📚 Related Documentation

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Service Account Setup](https://cloud.google.com/iam/docs/creating-managing-service-accounts)
- [Worky Database Schema](../migrations/001_initial_schema.sql)

## ✅ Success Checklist

- [ ] Python dependencies installed
- [ ] Service account JSON downloaded
- [ ] JSON file saved as `service_account.json`
- [ ] Google Sheet shared with service account
- [ ] `.env` file configured
- [ ] Database is running
- [ ] Loader script executed successfully

Once complete, verify data:
```bash
docker-compose exec db psql -U postgres -d worky -c "SELECT COUNT(*) FROM users;"
docker-compose exec db psql -U postgres -d worky -c "SELECT COUNT(*) FROM projects;"
```

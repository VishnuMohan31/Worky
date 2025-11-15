# ⚡ Google Sheets Loader - Quick Start

Load your project data from Google Sheets in 5 minutes!

## 📋 Prerequisites

- Database running (run `./start_db.sh` from root)
- Google account with access to the spreadsheet
- Python 3.11+

## 🚀 5-Minute Setup

### 1. Install Dependencies (1 min)

```bash
cd /Users/ravikiranponduri/Desktop/WIP/worky/db/db_loader
pip install -r requirements.txt
```

### 2. Get Service Account (2 min)

1. Go to https://console.cloud.google.com/
2. Create project → Enable "Google Sheets API" and "Google Drive API"
3. Create Service Account → Download JSON key
4. Save as `service_account.json` in this directory

### 3. Share Your Sheet (1 min)

1. Open: https://docs.google.com/spreadsheets/d/1bWsGB83O6GFZf2pRmm485it2X_XN1Rh8eCFs8knjHS0/
2. Click "Share"
3. Add the email from `service_account.json` (looks like: `name@project.iam.gserviceaccount.com`)
4. Give "Viewer" access
5. Click "Share"

### 4. Run Loader (1 min)

```bash
./load_sheets.sh
```

## ✅ Done!

Your data is now in the database. Verify:

```bash
# From root directory
docker-compose exec db psql -U postgres -d worky -c "SELECT COUNT(*) FROM users;"
docker-compose exec db psql -U postgres -d worky -c "SELECT COUNT(*) FROM projects;"
```

## 📊 Sheet Format

Your Google Sheet should have these sheets:

**Clients** (or "Client")
- Client Name
- Description
- Active

**Users** (or "Team", "People")
- Email
- Full Name
- Role

**Projects** (or "Project")
- Project Name
- Description
- Status
- Start Date
- End Date

**Tasks** (or "Task")
- Task Name
- Description
- Status
- Priority
- Assigned To (email)
- Due Date

## 🐛 Troubleshooting

**"Service account file not found"**
→ Make sure `service_account.json` is in `/Users/ravikiranponduri/Desktop/WIP/worky/db/db_loader/`

**"Permission denied"**
→ Share the Google Sheet with the service account email

**"Database connection failed"**
→ Run `./start_db.sh` from root directory

**"No sheet found"**
→ Rename your sheets to: Clients, Users, Projects, Tasks

## 📚 More Help

- [Full Setup Guide](../../GOOGLE_SHEETS_SETUP.md)
- [Detailed README](README.md)
- [Loader Source Code](load_from_sheets.py)

## 🎯 What Gets Loaded

- ✅ Clients → `clients` table
- ✅ Users → `users` table (password: "password")
- ✅ Projects → `projects` table
- ✅ Tasks → `tasks` table

All users can login with password: `password`

## 🔄 Re-run Anytime

Safe to run multiple times - only new data is added!

```bash
./load_sheets.sh
```

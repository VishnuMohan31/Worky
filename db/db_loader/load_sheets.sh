#!/bin/bash

echo "📊 Worky Data Loader - Google Sheets"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "load_from_sheets.py" ]; then
    echo "❌ Error: Must run from db/db_loader directory"
    exit 1
fi

# Check if service account file exists
if [ ! -f "service_account.json" ]; then
    echo "⚠️  Service account file not found!"
    echo ""
    echo "📝 Setup Instructions:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Enable Google Sheets API and Google Drive API"
    echo "3. Create a Service Account"
    echo "4. Download the JSON key"
    echo "5. Save it as 'service_account.json' in this directory"
    echo "6. Share your Google Sheet with the service account email"
    echo ""
    echo "See README.md for detailed instructions"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo "  Please edit .env if needed"
    echo ""
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import gspread" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if database is running
echo "Checking database connection..."
if ! docker-compose -f ../../docker-compose.yml ps db | grep -q "Up"; then
    echo "⚠️  Database is not running!"
    echo "  Start it with: cd ../.. && ./start_db.sh"
    exit 1
fi

echo ""
echo "🚀 Starting data load..."
echo ""

# Run the loader
python3 load_from_sheets.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Data load complete!"
    echo ""
    echo "📊 Verify data:"
    echo "  docker-compose exec db psql -U postgres -d worky -c 'SELECT COUNT(*) FROM users;'"
    echo "  docker-compose exec db psql -U postgres -d worky -c 'SELECT COUNT(*) FROM projects;'"
else
    echo ""
    echo "❌ Data load failed!"
    echo "  Check the error messages above"
    exit 1
fi

#!/bin/bash

echo "📊 Loading Data from Google Sheets..."
echo ""

# Check if database is running
if ! docker-compose ps db | grep -q "Up"; then
    echo "⚠️  Database is not running!"
    echo "   Starting database..."
    ./start_db.sh
    sleep 3
fi

# Check if migrations have been run
echo "Checking database..."
if ! docker-compose exec -T db psql -U postgres -d worky -c "\dt" 2>/dev/null | grep -q "users"; then
    echo "⚠️  Database not initialized!"
    echo "   Running migrations..."
    ./migrate_db.sh
fi

# Go to loader directory
cd db/db_loader

# Check if service account exists
if [ ! -f "service_account.json" ]; then
    echo ""
    echo "❌ Service account file not found!"
    echo ""
    echo "📝 Quick Setup:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Enable Google Sheets API and Google Drive API"
    echo "3. Create Service Account → Download JSON"
    echo "4. Save as: db/db_loader/service_account.json"
    echo "5. Share your Google Sheet with the service account email"
    echo ""
    echo "See GOOGLE_SHEETS_SETUP.md for detailed instructions"
    exit 1
fi

# Check dependencies
if ! python3 -c "import gspread" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run loader
echo ""
python3 load_from_sheets.py

cd ../..

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Data loaded successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "   ./start_api.sh    # Start API"
    echo "   cd ui && npm run dev  # Start UI"
    echo ""
    echo "   Then login at http://localhost:3007"
    echo "   Use any loaded user email with password: password"
else
    echo ""
    echo "❌ Data load failed!"
    exit 1
fi

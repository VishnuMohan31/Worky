#!/bin/bash

echo "=========================================="
echo "Worky Dummy Data Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create Excel templates
echo ""
echo "Creating Excel templates..."
python3 create_templates.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit Excel files in excel_templates/ directory"
echo "2. Add your dummy data to each file"
echo "3. Run: python3 load_data.py"
echo "=========================================="

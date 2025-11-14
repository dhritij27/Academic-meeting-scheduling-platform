#!/bin/bash

# Quick Start Script for Academic Meeting Scheduler
# This script automates the setup process

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Academic Meeting Scheduler - Quick Start                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

echo "1️⃣  Installing backend dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

echo "2️⃣  Checking .env file..."
if [ ! -f .env ]; then
    echo "Creating .env file with default settings..."
    cat > .env << EOF
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=academic_meetings
MYSQL_USER=root
MYSQL_PASSWORD=password
PORT=5000
EOF
    echo "✅ .env file created. Update credentials if needed."
else
    echo "✅ .env file already exists"
fi
echo ""

echo "3️⃣  Initializing database..."
echo "Running schema.sql..."
# Note: This requires MySQL to be running and proper credentials
mysql -u root -p < schema.sql 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database schema initialized"
else
    echo "⚠️  Database initialization failed. Make sure MySQL is running."
    echo "   Run manually: mysql -u root -p < backend/schema.sql"
fi
echo ""

echo "4️⃣  Seeding fake data..."
python seed_data.py
if [ $? -ne 0 ]; then
    echo "❌ Data seeding failed"
    exit 1
fi
echo "✅ Fake data seeded"
echo ""

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Start the backend server:"
echo "   python backend/app.py"
echo ""
echo "🌐 Start the frontend:"
echo "   Open index.html in your browser or use:"
echo "   python -m http.server 8000"
echo ""
echo "📝 Login with one of these accounts:"
echo "   • alice@university.edu"
echo "   • bob@university.edu"
echo "   • rajesh.kumar@university.edu"
echo ""
echo "📖 For more details, see SETUP_GUIDE.md"
echo ""

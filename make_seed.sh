#!/bin/bash

# Convenience script to seed the K12 LMS database
# This script activates the virtual environment and runs the seed script

set -e  # Exit on any error

echo "🌱 Starting K12 LMS database seeding..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "db" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected structure: backend/ and db/ directories should be present"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo "❌ Error: Virtual environment not found at backend/.venv"
    echo "   Please run: cd backend && python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source backend/.venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, sqlalchemy, passlib" 2>/dev/null || {
    echo "❌ Error: Required packages not installed"
    echo "   Please run: pip install -r backend/requirements.txt"
    exit 1
}

# Run the seed script
echo "🌱 Running database seed script..."
cd backend
python3 ../db/seed.py

echo "✅ Database seeding completed successfully!"
echo ""
echo "Demo credentials:"
echo "  Teacher: teacher@example.com / pass"
echo "  Student: student@example.com / pass"
echo ""
echo "You can now start the backend server with:"
echo "  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"

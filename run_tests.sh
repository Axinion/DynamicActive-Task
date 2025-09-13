#!/bin/bash

echo "🧪 K12 LMS Backend Smoke Tests"
echo "================================"

# Check if we're in the right directory
if [ ! -f "tests/test_auth_and_classes_flow.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected to find: tests/test_auth_and_classes_flow.py"
    exit 1
fi

# Check if backend virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo "❌ Error: Backend virtual environment not found"
    echo "   Please run: cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate backend virtual environment
echo "🔧 Activating backend virtual environment..."
source backend/.venv/bin/activate

# Check if test dependencies are installed
echo "📦 Checking test dependencies..."
if ! python3 -c "import pytest, httpx, fastapi" &> /dev/null; then
    echo "⚠️  Installing test dependencies..."
    pip install -r tests/requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install test dependencies"
        exit 1
    fi
fi

# Run the comprehensive smoke test
echo ""
echo "🚀 Running comprehensive auth and classes flow test..."
echo ""

python3 tests/test_auth_and_classes_flow.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed successfully!"
    echo ""
    echo "🎯 Quick Start Instructions:"
    echo "   1. Start backend: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
    echo "   2. Start frontend: cd frontend && npm run dev"
    echo "   3. Visit: http://localhost:3000"
    echo "   4. Login with demo credentials:"
    echo "      - Teacher: teacher@example.com / pass"
    echo "      - Student: student@example.com / pass"
    echo ""
    echo "🌱 To seed demo data: ./make_seed.sh"
else
    echo ""
    echo "❌ Tests failed. Please check the output above for details."
    exit 1
fi

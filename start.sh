#!/bin/bash
# Personal Finance Tracker - Start Script
# Simple script to start the application

echo "🚀 Starting Personal Finance Tracker..."
echo "=================================="

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found!"
    echo "   Make sure you're running this from the project directory."
    exit 1
fi

# Start the server
echo "🌐 Starting FastAPI server..."
echo "📱 Access your app at: http://localhost:8000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
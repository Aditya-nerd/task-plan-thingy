#!/bin/bash
# Smart Task Planner - Quick Run Script for Unix/Linux/macOS

echo "🎯 Starting Smart Task Planner..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment and run application
source venv/bin/activate
python main.py
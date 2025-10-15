#!/bin/bash
# Smart Task Planner - Unix/Linux/macOS Setup Script

echo "🎯 Smart Task Planner - Unix Setup"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔄 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "🔄 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp ".env.example" ".env"
    echo "✅ Created .env file from .env.example"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit the .env file to add your API keys:"
echo "   nano .env  # or use your preferred editor"
echo "2. Run the application:"
echo "   python main.py"
echo "3. Open http://localhost:8000 in your browser"
echo ""
echo "To activate the environment in the future, run:"
echo "   source venv/bin/activate"
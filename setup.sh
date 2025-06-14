#!/bin/bash

# Quiz Quest Backend Setup Script
# This script sets up the virtual environment and installs dependencies

echo "🎯 Quiz Quest Backend - Setup Script"
echo "====================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully!"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To run the backend server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the server: python start_server.py"
echo ""
echo "Or use the run script:"
echo "./run.sh"
echo ""
echo "📚 Once running, visit:"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Alternative Docs: http://localhost:8000/redoc"
echo "   • Health Check: http://localhost:8000/api/health" 
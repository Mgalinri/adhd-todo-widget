#!/bin/bash

# Setup script for ADHD To-Do Widget

echo "🎵 Setting up ADHD To-Do Widget..."

# Check if Python 3.9+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  source venv/bin/activate"
echo "  python main.py"
#!/bin/bash
# NexStep AI Pro - Automated Setup Script
# Author: Anubhab Mondal

set -e  # Exit on error

echo "🚀 NexStep AI Pro - Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION found"
    
    # Check if version is 3.8+
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
        echo "⚠️  Warning: Python 3.8+ recommended. You have $PYTHON_VERSION"
    fi
else
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"

echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.template .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your Google API key!"
    echo "   Get your API key at: https://makersuite.google.com/app/apikey"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📝 Next Steps:"
echo "1. Edit .env file and add your GOOGLE_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the app: streamlit run nexstep_pro.py"
echo ""
echo "💡 Quick start:"
echo "   source venv/bin/activate && streamlit run nexstep_pro.py"
echo ""
echo "📚 For deployment instructions, see DEPLOYMENT.md"
echo "📖 For full documentation, see README.md"
echo ""
echo "🎉 Happy career planning!"
echo ""

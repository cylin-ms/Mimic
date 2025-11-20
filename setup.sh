#!/bin/bash

echo "🚀 Setting up Mimic..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "📦 Virtual environment already exists."
fi

# Activate and install
echo "⬇️ Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Download model
echo "⬇️ Checking AI Model..."
python download_model.py

echo "✅ Setup complete!"
echo ""
echo "To run the estimator:"
echo "  source venv/bin/activate"
echo "  python estimate_value.py <your_calendar.json>"

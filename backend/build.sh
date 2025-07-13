#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting Render deployment..."

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test imports
echo "🧪 Testing imports..."
python test_render.py

echo "✅ Build completed successfully!" 
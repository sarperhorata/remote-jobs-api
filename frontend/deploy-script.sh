#!/bin/bash

# Buzz2Remote Frontend Deployment Script
# Handles timeout issues and ensures proper testing

set -e  # Exit on any error

echo "🚀 Starting Buzz2Remote Frontend Deployment"

# Function to run commands with timeout
run_with_timeout() {
    local timeout=$1
    local cmd="$2"
    local desc="$3"
    
    echo "⏱️  Running: $desc (timeout: ${timeout}s)"
    
    # Use timeout command (different on macOS vs Linux)
    if command -v gtimeout >/dev/null 2>&1; then
        gtimeout $timeout bash -c "$cmd" || {
            echo "❌ $desc timed out after ${timeout}s"
            return 1
        }
    elif command -v timeout >/dev/null 2>&1; then
        timeout $timeout bash -c "$cmd" || {
            echo "❌ $desc timed out after ${timeout}s"
            return 1
        }
    else
        # Fallback for macOS without coreutils
        eval "$cmd" || {
            echo "❌ $desc failed"
            return 1
        }
    fi
    
    echo "✅ $desc completed successfully"
}

# Install coreutils for macOS timeout
if [[ "$OSTYPE" == "darwin"* ]] && ! command -v gtimeout >/dev/null 2>&1; then
    echo "📦 Installing coreutils for timeout command..."
    if command -v brew >/dev/null 2>&1; then
        brew install coreutils 2>/dev/null || echo "⚠️  Please install coreutils manually: brew install coreutils"
    else
        echo "⚠️  Please install Homebrew and then: brew install coreutils"
    fi
fi

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    echo "❌ Not in frontend directory! Please run from frontend folder."
    exit 1
fi

# Kill any hanging processes
echo "🧹 Cleaning up existing processes..."
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "node.*3000" 2>/dev/null || true

# Install dependencies if needed
if [[ ! -d "node_modules" ]] || [[ ! -f "node_modules/.package-lock.json" ]]; then
    echo "📦 Installing dependencies..."
    run_with_timeout 120 "npm install" "Dependencies installation"
fi

# Run tests with timeout
echo "🧪 Running tests..."
run_with_timeout 60 "NODE_OPTIONS=\"--openssl-legacy-provider\" npm run test -- --watchAll=false --silent --maxWorkers=2" "Test execution"

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s "http://localhost:8001/health" >/dev/null 2>&1; then
    echo "✅ Backend is running on port 8001"
else
    echo "⚠️  Backend not detected on port 8001"
    echo "   Please start backend: cd ../backend && uvicorn main:app --reload --host 0.0.0.0 --port 8001"
fi

# Test API connectivity
echo "🔗 Testing API connectivity..."
if curl -s "http://localhost:8001/api/jobs/statistics" | grep -q "positions" 2>/dev/null; then
    echo "✅ API statistics endpoint working - autocomplete should work"
else
    echo "⚠️  API statistics endpoint issue - autocomplete might use fallback data"
fi

# Start frontend with proper environment
echo "🌐 Starting frontend..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Press Ctrl+C to stop"

# Check if port 3000 is already in use
if lsof -i :3000 >/dev/null 2>&1; then
    echo "⚠️  Port 3000 is already in use"
    echo "   The development server will ask you to use a different port"
fi

# Start the development server
NODE_OPTIONS="--openssl-legacy-provider" npm start

echo "🎉 Deployment script completed!" 
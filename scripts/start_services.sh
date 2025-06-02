#!/bin/bash

# Buzz2Remote Services Startup Script
# Bu script tüm servisleri düzgün sırayla başlatır

set -e

echo "🚀 Buzz2Remote Services Startup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if port is available
check_port_available() {
    local port=$1
    local service=$2
    
    if lsof -i :$port > /dev/null 2>&1; then
        print_status $YELLOW "⚠️  Port $port ($service) is in use, cleaning up..."
        
        # Kill processes using the port
        lsof -ti :$port | xargs -r kill -9 2>/dev/null || true
        sleep 2
        
        if lsof -i :$port > /dev/null 2>&1; then
            print_status $RED "❌ Could not free port $port"
            return 1
        else
            print_status $GREEN "✅ Port $port is now available"
        fi
    else
        print_status $GREEN "✅ Port $port ($service) is available"
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service=$2
    local max_attempts=30
    local attempt=1
    
    print_status $BLUE "⏳ Waiting for $service to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
            print_status $GREEN "✅ $service is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_status $RED "❌ $service failed to start after $max_attempts attempts"
    return 1
}

# Cleanup any existing processes
print_status $BLUE "🧹 Cleaning up existing processes..."
./scripts/cleanup_processes.sh > /dev/null 2>&1 || true

# Check and prepare ports
print_status $BLUE "🌐 Checking ports..."
check_port_available 8001 "Backend"
check_port_available 3000 "Frontend"

echo ""
print_status $BLUE "🔧 Starting Backend Service..."
echo "================================="

# Start Backend with Bot Manager
cd backend
export TESTING=false  # Enable Telegram bot
nohup uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid

print_status $GREEN "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
if wait_for_service "http://localhost:8001/health" "Backend"; then
    print_status $GREEN "✅ Backend is healthy and ready!"
else
    print_status $RED "❌ Backend failed to start"
    exit 1
fi

echo ""
print_status $BLUE "⚛️  Starting Frontend Service..."
echo "=================================="

# Start Frontend
cd ../frontend
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

print_status $GREEN "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to be ready
if wait_for_service "http://localhost:3000" "Frontend"; then
    print_status $GREEN "✅ Frontend is ready!"
else
    print_status $YELLOW "⚠️  Frontend may still be starting..."
fi

echo ""
print_status $GREEN "🎉 Services Startup Summary"
print_status $GREEN "=========================="
print_status $GREEN "✅ Backend:  http://localhost:8001 (PID: $BACKEND_PID)"
print_status $GREEN "✅ Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
print_status $GREEN "✅ Admin:    http://localhost:8001/admin"
print_status $GREEN "✅ API Docs: http://localhost:8001/docs"

echo ""
print_status $BLUE "📋 Service Management:"
echo "  🛑 Stop services: ./scripts/stop_services.sh"
echo "  📊 Check status:  ./scripts/check_status.sh"
echo "  📝 View logs:     tail -f logs/*.log"

echo ""
print_status $GREEN "🚀 All services are up and running!" 
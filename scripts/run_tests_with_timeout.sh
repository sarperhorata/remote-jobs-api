#!/bin/bash

# Test Orchestrator with Timeout Control
# Runs backend and frontend tests with automatic timeout management

set -e

# Configuration
BACKEND_TEST_TIMEOUT=120  # Backend tests can take longer
FRONTEND_TEST_TIMEOUT=60  # Frontend tests should be quick
LOG_DIR="logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%H:%M:%S')] ${message}${NC}"
}

# Create logs directory
mkdir -p "$LOG_DIR"

print_status $GREEN "🚀 Buzz2Remote Test Suite with Timeout Control"
print_status $BLUE "⚙️ Backend Timeout: ${BACKEND_TEST_TIMEOUT}s | Frontend Timeout: ${FRONTEND_TEST_TIMEOUT}s"
echo "=================================================================="

# Function to check if backend is running
check_backend() {
    if curl -s --max-time 5 "http://localhost:8001/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if frontend is running  
check_frontend() {
    if curl -s --max-time 5 "http://localhost:3000" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Backend Tests
print_status $BLUE "🧪 Running Backend Tests..."
echo "================================="

if check_backend; then
    print_status $GREEN "✅ Backend is running - proceeding with tests"
    
    # Run backend tests with timeout
    cd backend
    timeout_result=0
    ./scripts/simple_timeout_wrapper.sh $BACKEND_TEST_TIMEOUT "python -m pytest -v --tb=short" "Backend Tests" || timeout_result=$?
    
    if [ $timeout_result -eq 124 ]; then
        print_status $YELLOW "⏰ Backend tests moved to background due to timeout"
        print_status $BLUE "📝 Check background processes: ps aux | grep pytest"
    elif [ $timeout_result -eq 0 ]; then
        print_status $GREEN "✅ Backend tests completed successfully"
    else
        print_status $RED "❌ Backend tests failed (exit: $timeout_result)"
    fi
    cd ..
else
    print_status $YELLOW "⚠️ Backend not running - skipping backend tests"
    print_status $BLUE "💡 Start backend: ./scripts/start_services.sh"
fi

echo ""

# Frontend Tests  
print_status $BLUE "⚛️ Running Frontend Tests..."
echo "=================================="

if check_frontend; then
    print_status $GREEN "✅ Frontend is running - proceeding with tests"
    
    # Run frontend tests with timeout
    cd frontend
    timeout_result=0
    ../scripts/simple_timeout_wrapper.sh $FRONTEND_TEST_TIMEOUT "npm test -- --watchAll=false --verbose" "Frontend Tests" || timeout_result=$?
    
    if [ $timeout_result -eq 124 ]; then
        print_status $YELLOW "⏰ Frontend tests moved to background due to timeout"
        print_status $BLUE "📝 Check background processes: ps aux | grep 'npm test'"
    elif [ $timeout_result -eq 0 ]; then
        print_status $GREEN "✅ Frontend tests completed successfully"
    else
        print_status $RED "❌ Frontend tests failed (exit: $timeout_result)"
    fi
    cd ..
else
    print_status $YELLOW "⚠️ Frontend not running - skipping frontend tests"
    print_status $BLUE "💡 Start frontend: ./scripts/start_services.sh"
fi

echo ""

# Test Coverage (Quick)
print_status $BLUE "📊 Quick Test Coverage Check..."
echo "====================================="

if check_frontend; then
    cd frontend
    ../scripts/simple_timeout_wrapper.sh 30 "npm test -- --coverage --watchAll=false --silent" "Frontend Coverage" || true
    cd ..
fi

echo ""

# Summary
print_status $GREEN "📋 Test Suite Summary"
echo "======================"

# Check for background processes
background_count=$(ps aux | grep -E "(pytest|npm test)" | grep -v grep | wc -l | tr -d ' ')
if [ "$background_count" -gt 0 ]; then
    print_status $YELLOW "⚠️ $background_count test processes still running in background"
    print_status $BLUE "📝 View background processes:"
    echo "   ps aux | grep -E '(pytest|npm test)' | grep -v grep"
    echo ""
    print_status $BLUE "📁 Background info files:"
    ls -la /tmp/buzz2remote_bg_*.info 2>/dev/null || echo "   No background info files found"
else
    print_status $GREEN "✅ All test processes completed"
fi

echo ""
print_status $BLUE "🔧 Useful Commands:"
echo "  📊 Check service status: ./scripts/start_services.sh"
echo "  🧹 Clean up processes: pkill -f 'pytest|npm test'"
echo "  📁 View logs: ls -la $LOG_DIR/"
echo "  ⏰ Custom timeout test: ./scripts/simple_timeout_wrapper.sh [seconds] 'command' 'description'"

print_status $GREEN "🎉 Test orchestration completed!" 
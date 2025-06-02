#!/bin/bash

# Process Cleanup and Health Check Script
# Bu script zombie process'leri temizler ve sistem sağlığını kontrol eder

set -e

echo "🧹 Process Cleanup and Health Check"
echo "=================================="

# Function to kill processes safely
kill_process_group() {
    local pattern=$1
    local description=$2
    
    echo "🔍 Checking for $description..."
    pids=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}' | head -10)
    
    if [ -n "$pids" ]; then
        echo "📋 Found processes: $pids"
        for pid in $pids; do
            if kill -0 $pid 2>/dev/null; then
                echo "🔄 Stopping PID $pid..."
                kill -TERM $pid 2>/dev/null || true
                sleep 2
                if kill -0 $pid 2>/dev/null; then
                    echo "⚠️  Force killing PID $pid..."
                    kill -9 $pid 2>/dev/null || true
                fi
            fi
        done
        echo "✅ $description cleanup completed"
    else
        echo "✅ No $description processes found"
    fi
}

# Function to check port availability
check_port() {
    local port=$1
    local service=$2
    
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Port $port ($service) is in use"
        lsof -i :$port | grep LISTEN || true
    else
        echo "✅ Port $port ($service) is available"
    fi
}

# Kill zombie processes
echo "🧟 Cleaning zombie processes..."

# Clean test processes
kill_process_group "pytest|python.*test" "Test processes"

# Clean duplicate backend processes
kill_process_group "python main\.py|uvicorn.*main" "Backend processes"

# Clean duplicate frontend processes (keep only newest)
echo "🔍 Managing frontend processes..."
frontend_pids=$(ps aux | grep -E "npm start|react-scripts" | grep -v grep | awk '{print $2}' | sort -n)
if [ -n "$frontend_pids" ]; then
    frontend_count=$(echo "$frontend_pids" | wc -l | tr -d ' ')
    if [ $frontend_count -gt 3 ]; then
        echo "⚠️  Too many frontend processes ($frontend_count), keeping newest 3..."
        old_pids=$(echo "$frontend_pids" | head -n $(($frontend_count - 3)))
        for pid in $old_pids; do
            echo "🔄 Stopping old frontend PID $pid..."
            kill -TERM $pid 2>/dev/null || true
        done
    else
        echo "✅ Frontend process count is normal ($frontend_count)"
    fi
fi

# Clean Telegram bot conflicts
kill_process_group "telegram.*bot|python.*telegram" "Telegram bot processes"

echo ""
echo "🌐 Port Status Check"
echo "==================="
check_port 8001 "Backend"
check_port 3000 "Frontend"

echo ""
echo "📊 System Resource Usage"
echo "========================"
echo "Memory Usage:"
ps aux | awk 'NR>1 {sum+=$6} END {printf "Total: %.1f MB\n", sum/1024}'

echo "Active Python Processes:"
ps aux | grep python | grep -v grep | wc -l | awk '{print $1 " processes"}'

echo "Active Node Processes:"
ps aux | grep node | grep -v grep | wc -l | awk '{print $1 " processes"}'

echo ""
echo "✅ Cleanup completed! System is ready for fresh start." 
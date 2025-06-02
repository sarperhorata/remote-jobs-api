#!/bin/bash

# Terminal Command Timeout Monitor
# Monitors running commands and automatically backgrounds those exceeding 60 seconds
# Excludes long-running services (BE/FE servers)

set -euo pipefail

# Configuration
TIMEOUT_SECONDS=60
LOG_DIR="logs"
MONITOR_INTERVAL=5
PID_DIR="/tmp/buzz2remote_monitor"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%H:%M:%S')] ${message}${NC}"
}

log_event() {
    local event="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $event" >> "$LOG_DIR/command_monitor.log"
}

# Function to check if process is a long-running service
is_long_running_service() {
    local cmd="$1"
    case "$cmd" in
        *"uvicorn"*|*"npm start"*|*"python -m"*|*"nodemon"*|*"webpack-dev-server"*)
            return 0  # True - is long-running service
            ;;
        *)
            return 1  # False - not a long-running service
            ;;
    esac
}

# Function to get process command line
get_process_cmd() {
    local pid="$1"
    if ps -p "$pid" > /dev/null 2>&1; then
        ps -p "$pid" -o command= 2>/dev/null || echo "unknown"
    else
        echo "terminated"
    fi
}

# Function to track a new command
track_command() {
    local pid="$1"
    local cmd="$2"
    local start_time="$3"
    
    local track_file="$PID_DIR/${pid}.track"
    echo "PID=$pid" > "$track_file"
    echo "CMD=$cmd" >> "$track_file"
    echo "START_TIME=$start_time" >> "$track_file"
    echo "STATUS=running" >> "$track_file"
    
    log_event "TRACKING: PID $pid - $cmd"
    print_status $BLUE "🔍 Tracking command: PID $pid"
}

# Function to background a command
background_command() {
    local pid="$1"
    local cmd="$2"
    local runtime="$3"
    
    print_status $YELLOW "⏰ Command exceeded ${TIMEOUT_SECONDS}s timeout (${runtime}s)"
    print_status $YELLOW "📝 Command: $cmd"
    print_status $YELLOW "🔄 Moving PID $pid to background..."
    
    # Send SIGTSTP to background the process
    kill -TSTP "$pid" 2>/dev/null || true
    sleep 1
    # Send SIGCONT to continue in background
    kill -CONT "$pid" 2>/dev/null || true
    
    # Update track file
    local track_file="$PID_DIR/${pid}.track"
    if [[ -f "$track_file" ]]; then
        if sed -i '' 's/STATUS=running/STATUS=backgrounded/' "$track_file" 2>/dev/null; then
            :  # macOS version worked
        else
            sed -i 's/STATUS=running/STATUS=backgrounded/' "$track_file"  # Linux version
        fi
        echo "BACKGROUND_TIME=$(date +%s)" >> "$track_file"
    fi
    
    log_event "BACKGROUNDED: PID $pid after ${runtime}s - $cmd"
    print_status $GREEN "✅ Command backgrounded successfully"
}

# Function to check running commands
check_commands() {
    local current_time=$(date +%s)
    
    # Get all tracked processes
    for track_file in "$PID_DIR"/*.track 2>/dev/null; do
        [[ -f "$track_file" ]] || continue
        
        local pid=""
        local cmd=""
        local start_time=""
        local status=""
        
        # Source the track file
        while IFS='=' read -r key value; do
            case "$key" in
                PID) pid="$value" ;;
                CMD) cmd="$value" ;;
                START_TIME) start_time="$value" ;;
                STATUS) status="$value" ;;
            esac
        done < "$track_file"
        
        # Skip if already backgrounded or invalid data
        [[ "$status" == "running" && -n "$pid" && -n "$start_time" ]] || continue
        
        # Check if process still exists
        if ! ps -p "$pid" > /dev/null 2>&1; then
            print_status $GREEN "✅ Command completed: PID $pid"
            log_event "COMPLETED: PID $pid - $cmd"
            rm -f "$track_file"
            continue
        fi
        
        # Calculate runtime
        local runtime=$((current_time - start_time))
        
        # Check if it's a long-running service
        if is_long_running_service "$cmd"; then
            print_status $BLUE "🔄 Ignoring long-running service: PID $pid ($cmd)"
            rm -f "$track_file"  # Don't track services
            continue
        fi
        
        # Check timeout
        if [[ $runtime -gt $TIMEOUT_SECONDS ]]; then
            background_command "$pid" "$cmd" "$runtime"
        else
            local remaining=$((TIMEOUT_SECONDS - runtime))
            if [[ $((runtime % 20)) -eq 0 ]]; then  # Show progress every 20 seconds
                print_status $YELLOW "⏳ PID $pid: ${runtime}s elapsed, ${remaining}s remaining"
            fi
        fi
    done
}

# Function to show status
show_status() {
    print_status $BLUE "📊 Command Monitor Status"
    echo "=========================="
    
    local active_count=0
    local backgrounded_count=0
    
    for track_file in "$PID_DIR"/*.track 2>/dev/null; do
        [[ -f "$track_file" ]] || continue
        
        local pid=""
        local cmd=""
        local start_time=""
        local status=""
        
        while IFS='=' read -r key value; do
            case "$key" in
                PID) pid="$value" ;;
                CMD) cmd="$value" ;;
                START_TIME) start_time="$value" ;;
                STATUS) status="$value" ;;
            esac
        done < "$track_file"
        
        if ps -p "$pid" > /dev/null 2>&1; then
            local runtime=$(($(date +%s) - start_time))
            if [[ "$status" == "backgrounded" ]]; then
                echo "🔄 PID $pid: BACKGROUNDED (${runtime}s) - ${cmd:0:60}..."
                backgrounded_count=$((backgrounded_count + 1))
            else
                echo "⏳ PID $pid: RUNNING (${runtime}s) - ${cmd:0:60}..."
                active_count=$((active_count + 1))
            fi
        else
            rm -f "$track_file"
        fi
    done
    
    echo ""
    echo "Active: $active_count | Backgrounded: $backgrounded_count"
    echo "Timeout: ${TIMEOUT_SECONDS}s | Check interval: ${MONITOR_INTERVAL}s"
}

# Function to cleanup old files
cleanup() {
    print_status $YELLOW "🧹 Cleaning up monitor files..."
    
    for track_file in "$PID_DIR"/*.track 2>/dev/null; do
        [[ -f "$track_file" ]] || continue
        
        local pid=""
        while IFS='=' read -r key value; do
            [[ "$key" == "PID" ]] && pid="$value"
        done < "$track_file"
        
        if [[ -n "$pid" ]] && ! ps -p "$pid" > /dev/null 2>&1; then
            rm -f "$track_file"
        fi
    done
    
    log_event "CLEANUP: Removed stale tracking files"
    print_status $GREEN "✅ Cleanup completed"
}

# Main monitoring loop
monitor_loop() {
    print_status $GREEN "🚀 Starting command timeout monitor"
    print_status $BLUE "⚙️  Timeout: ${TIMEOUT_SECONDS}s | Interval: ${MONITOR_INTERVAL}s"
    log_event "MONITOR_START: Timeout=${TIMEOUT_SECONDS}s"
    
    while true; do
        check_commands
        sleep $MONITOR_INTERVAL
    done
}

# Function to start monitoring a command
start_monitoring() {
    local cmd="$1"
    local description="${2:-Command}"
    
    print_status $BLUE "🔄 Starting monitored command: $description"
    print_status $YELLOW "📝 Command: $cmd"
    
    # Start command in background
    eval "$cmd" &
    local pid=$!
    local start_time=$(date +%s)
    
    # Track the command
    track_command "$pid" "$cmd" "$start_time"
    
    print_status $GREEN "🚀 Command started with PID: $pid"
    return $pid
}

# Command line interface
case "${1:-}" in
    "monitor")
        monitor_loop
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup
        ;;
    "start")
        if [[ $# -lt 2 ]]; then
            echo "Usage: $0 start 'command' [description]"
            exit 1
        fi
        start_monitoring "$2" "${3:-}"
        ;;
    "stop")
        print_status $YELLOW "🛑 Stopping all monitored commands..."
        for track_file in "$PID_DIR"/*.track 2>/dev/null; do
            [[ -f "$track_file" ]] || continue
            
            local pid=""
            while IFS='=' read -r key value; do
                [[ "$key" == "PID" ]] && pid="$value"
            done < "$track_file"
            
            if [[ -n "$pid" ]] && ps -p "$pid" > /dev/null 2>&1; then
                print_status $BLUE "🔄 Stopping PID $pid..."
                kill -TERM "$pid" 2>/dev/null || true
            fi
            rm -f "$track_file"
        done
        log_event "MONITOR_STOP: All commands stopped"
        print_status $GREEN "✅ All monitored commands stopped"
        ;;
    *)
        echo "Command Timeout Monitor"
        echo "======================"
        echo ""
        echo "Usage: $0 {monitor|status|cleanup|start|stop}"
        echo ""
        echo "Commands:"
        echo "  monitor           - Start monitoring loop"
        echo "  status            - Show current status"
        echo "  cleanup           - Clean up old tracking files"
        echo "  start 'cmd' [desc] - Start monitoring a command"
        echo "  stop              - Stop all monitored commands"
        echo ""
        echo "Configuration:"
        echo "  Timeout: ${TIMEOUT_SECONDS} seconds"
        echo "  Log dir: ${LOG_DIR}"
        echo "  PID dir: ${PID_DIR}"
        echo ""
        echo "Examples:"
        echo "  $0 start 'npm test' 'Frontend Tests'"
        echo "  $0 start 'python -m pytest' 'Backend Tests'"
        echo "  $0 monitor  # Start in background: nohup $0 monitor > monitor.log 2>&1 &"
        ;;
esac 
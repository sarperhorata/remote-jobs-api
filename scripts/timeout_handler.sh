#!/bin/bash

# Timeout Handler for Long-Running Commands
# 60 saniyeden uzun süren komutları otomatik arka plana alır

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to run command with timeout and background handling
run_with_timeout() {
    local cmd="$1"
    local timeout_seconds="${2:-60}"
    local description="${3:-Command}"
    local background_after="${4:-true}"
    
    print_status $BLUE "🔄 Running: $description"
    print_status $YELLOW "⏱️  Timeout: ${timeout_seconds}s, Background: $background_after"
    
    # Create a temporary file for the command output
    local temp_log="/tmp/buzz2remote_cmd_$$.log"
    local pid_file="/tmp/buzz2remote_pid_$$.pid"
    
    # Start command in background and capture PID
    (
        eval "$cmd" 2>&1 | tee "$temp_log"
        echo $? > "/tmp/buzz2remote_exit_$$"
    ) &
    local cmd_pid=$!
    echo $cmd_pid > "$pid_file"
    
    print_status $GREEN "🚀 Started with PID: $cmd_pid"
    
    # Monitor the command
    local elapsed=0
    local check_interval=2
    
    while [ $elapsed -lt $timeout_seconds ]; do
        if ! kill -0 $cmd_pid 2>/dev/null; then
            # Command finished
            local exit_code=0
            if [ -f "/tmp/buzz2remote_exit_$$" ]; then
                exit_code=$(cat "/tmp/buzz2remote_exit_$$")
                rm -f "/tmp/buzz2remote_exit_$$"
            fi
            
            print_status $GREEN "✅ $description completed in ${elapsed}s (exit: $exit_code)"
            
            # Show last few lines of output
            if [ -f "$temp_log" ]; then
                echo ""
                print_status $BLUE "📋 Last 5 lines of output:"
                tail -5 "$temp_log"
                rm -f "$temp_log"
            fi
            
            rm -f "$pid_file"
            return $exit_code
        fi
        
        sleep $check_interval
        elapsed=$((elapsed + check_interval))
        
        # Show progress dots
        echo -n "."
        
        # Show periodic status
        if [ $((elapsed % 20)) -eq 0 ] && [ $elapsed -gt 0 ]; then
            echo ""
            print_status $YELLOW "⏳ Still running... ${elapsed}s elapsed"
        fi
    done
    
    echo ""
    
    if [ "$background_after" = "true" ]; then
        print_status $YELLOW "⏰ Timeout reached (${timeout_seconds}s) - Moving to background"
        print_status $BLUE "📁 PID file: $pid_file"
        print_status $BLUE "📝 Log file: $temp_log"
        print_status $GREEN "🔧 Monitor with: tail -f $temp_log"
        print_status $GREEN "🛑 Stop with: kill \$(cat $pid_file)"
        
        # Return special exit code to indicate background operation
        return 124
    else
        print_status $RED "⏰ Timeout reached - Killing process"
        kill -TERM $cmd_pid 2>/dev/null || true
        sleep 3
        kill -9 $cmd_pid 2>/dev/null || true
        
        rm -f "$temp_log" "$pid_file"
        return 124
    fi
}

# Function to check background processes
check_background_processes() {
    print_status $BLUE "🔍 Checking background processes..."
    
    local found_any=false
    for pid_file in /tmp/buzz2remote_pid_*.pid; do
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            local log_file="/tmp/buzz2remote_cmd_${pid_file##*/}"; log_file="${log_file%.pid}.log"
            
            if kill -0 $pid 2>/dev/null; then
                print_status $GREEN "✅ PID $pid still running"
                print_status $BLUE "   📝 Log: $log_file"
                found_any=true
            else
                print_status $YELLOW "⚰️  PID $pid finished - cleaning up"
                rm -f "$pid_file"
                [ -f "$log_file" ] && rm -f "$log_file"
            fi
        fi
    done
    
    if [ "$found_any" = false ]; then
        print_status $GREEN "✅ No background processes found"
    fi
}

# Function to stop all background processes
stop_all_background() {
    print_status $YELLOW "🛑 Stopping all background processes..."
    
    for pid_file in /tmp/buzz2remote_pid_*.pid; do
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 $pid 2>/dev/null; then
                print_status $BLUE "🔄 Stopping PID $pid..."
                kill -TERM $pid 2>/dev/null || true
                sleep 2
                kill -9 $pid 2>/dev/null || true
            fi
            rm -f "$pid_file"
        fi
    done
    
    # Clean up log files
    rm -f /tmp/buzz2remote_cmd_*.log
    rm -f /tmp/buzz2remote_exit_*
    
    print_status $GREEN "✅ All background processes stopped"
}

# Export functions for use in other scripts
export -f run_with_timeout
export -f check_background_processes
export -f stop_all_background
export -f print_status

# If script is called directly, show usage
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    case "${1:-}" in
        "check")
            check_background_processes
            ;;
        "stop")
            stop_all_background
            ;;
        "test")
            # Test the timeout handler
            print_status $BLUE "🧪 Testing timeout handler..."
            run_with_timeout "sleep 10 && echo 'Command completed!'" 5 "Test sleep command" true
            ;;
        *)
            echo "Usage: $0 {check|stop|test}"
            echo ""
            echo "Functions available for sourcing:"
            echo "  run_with_timeout 'command' [timeout_sec] [description] [background_after]"
            echo "  check_background_processes"
            echo "  stop_all_background"
            echo ""
            echo "Example:"
            echo "  source $0"
            echo "  run_with_timeout 'npm test' 60 'Frontend Tests' true"
            ;;
    esac
fi 
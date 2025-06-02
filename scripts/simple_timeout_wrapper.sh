#!/bin/bash

# Simple Terminal Timeout Wrapper
# Usage: ./simple_timeout_wrapper.sh [timeout_seconds] "command" "description"

TIMEOUT_SECONDS=${1:-60}
COMMAND=${2:-"echo 'No command specified'"}
DESCRIPTION=${3:-"Command"}

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

print_status $BLUE "🔄 Starting: $DESCRIPTION"
print_status $YELLOW "⏱️ Timeout: ${TIMEOUT_SECONDS}s"
print_status $YELLOW "📝 Command: $COMMAND"

# Start command and capture PID
eval "$COMMAND" &
CMD_PID=$!

print_status $GREEN "🚀 Started with PID: $CMD_PID"

# Monitor the command
elapsed=0
check_interval=2

while [ $elapsed -lt $TIMEOUT_SECONDS ]; do
    if ! kill -0 $CMD_PID 2>/dev/null; then
        # Command finished
        wait $CMD_PID
        exit_code=$?
        print_status $GREEN "✅ $DESCRIPTION completed in ${elapsed}s (exit: $exit_code)"
        exit $exit_code
    fi
    
    sleep $check_interval
    elapsed=$((elapsed + check_interval))
    
    # Show progress every 20 seconds
    if [ $((elapsed % 20)) -eq 0 ] && [ $elapsed -gt 0 ]; then
        print_status $YELLOW "⏳ Still running... ${elapsed}s elapsed"
    fi
done

# Timeout reached
print_status $YELLOW "⏰ Timeout reached (${TIMEOUT_SECONDS}s)"
print_status $BLUE "🔄 Moving to background..."

# Create background info file
bg_info_file="/tmp/buzz2remote_bg_${CMD_PID}.info"
cat > "$bg_info_file" << EOF
PID: $CMD_PID
Command: $COMMAND
Description: $DESCRIPTION
Started: $(date)
Backgrounded: $(date)
EOF

print_status $GREEN "📁 Background info: $bg_info_file"
print_status $GREEN "🛑 Stop with: kill $CMD_PID"

# Keep running in background
print_status $GREEN "✅ Command moved to background successfully"
exit 124  # Special exit code for timeout 
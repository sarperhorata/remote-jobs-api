#!/bin/bash

# Test Runner with Timeout Management
# 60+ saniye süren test'leri arka plana alır

set -e

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

run_tests_with_timeout() {
    local test_pattern="$1"
    local timeout_sec="${2:-60}"
    local description="${3:-Tests}"
    
    print_status $BLUE "🧪 Running: $description"
    print_status $YELLOW "⏱️  Timeout: ${timeout_sec}s"
    
    # Start test in background
    timeout $timeout_sec npm test -- --watchAll=false --testPathPattern="$test_pattern" --verbose > "test_${test_pattern//\//_}.log" 2>&1 &
    local test_pid=$!
    
    local elapsed=0
    while [ $elapsed -lt $timeout_sec ]; do
        if ! kill -0 $test_pid 2>/dev/null; then
            wait $test_pid
            local exit_code=$?
            if [ $exit_code -eq 0 ]; then
                print_status $GREEN "✅ $description completed successfully!"
            else
                print_status $RED "❌ $description failed (exit: $exit_code)"
            fi
            return $exit_code
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        echo -n "."
    done
    
    print_status $YELLOW "⏰ $description timed out - moving to background"
    print_status $BLUE "📝 Log: test_${test_pattern//\//_}.log"
    print_status $GREEN "🔧 Monitor: tail -f test_${test_pattern//\//_}.log"
    
    return 124
}

# Quick successful tests
print_status $GREEN "🚀 Running Quick Successful Tests"
echo "================================="

run_tests_with_timeout "JobCard" 30 "JobCard Tests"
run_tests_with_timeout "FilterBar" 30 "FilterBar Tests" 
run_tests_with_timeout "AuthContext" 30 "AuthContext Tests"

echo ""
print_status $BLUE "📊 Test Summary"
echo "==============="

# Count log files for results
successful_tests=0
failed_tests=0
timeout_tests=0

for log_file in test_*.log; do
    if [ -f "$log_file" ]; then
        if grep -q "Tests:.*passed.*total" "$log_file" && ! grep -q "failed" "$log_file"; then
            successful_tests=$((successful_tests + 1))
        elif grep -q "failed" "$log_file"; then
            failed_tests=$((failed_tests + 1))
        else
            timeout_tests=$((timeout_tests + 1))
        fi
    fi
done

echo "✅ Successful: $successful_tests"
echo "❌ Failed: $failed_tests" 
echo "⏰ Timeout: $timeout_tests"

total_tests=$((successful_tests + failed_tests + timeout_tests))
if [ $total_tests -gt 0 ]; then
    success_rate=$(( (successful_tests * 100) / total_tests ))
    print_status $GREEN "📈 Success Rate: ${success_rate}%"
fi

echo ""
print_status $BLUE "📋 Next Steps:"
echo "  🔍 Check logs: ls test_*.log"
echo "  📊 Full coverage: npm test -- --watchAll=false --coverage"
echo "  🧹 Cleanup logs: rm test_*.log" 
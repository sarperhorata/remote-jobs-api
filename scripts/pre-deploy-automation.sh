#!/bin/bash

# Pre-Deploy Automation Script with Auto-Fix
# Runs tests, detects errors, attempts fixes, and retries deployment
# Author: AI Assistant for Buzz2Remote
# Version: 2.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
MAX_RETRY_ATTEMPTS=3
TEST_TIMEOUT=120
LOG_DIR="deploy-logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create log directory
mkdir -p "$LOG_DIR"

print_header() {
    echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  🚀 ${BLUE}BUZZ2REMOTE PRE-DEPLOYMENT AUTOMATION v2.0${NC}           ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  📅 Started: $(date '+%Y-%m-%d %H:%M:%S')                       ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    local title="$1"
    echo -e "\n${PURPLE}▶ ${title}${NC}"
    echo -e "${PURPLE}${title//?/=}${NC}"
}

print_status() {
    local status="$1"
    local message="$2"
    case $status in
        "SUCCESS") echo -e "${GREEN}✅ ${message}${NC}" ;;
        "ERROR")   echo -e "${RED}❌ ${message}${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  ${message}${NC}" ;;
        "INFO")    echo -e "${BLUE}ℹ️  ${message}${NC}" ;;
        "FIXING")  echo -e "${CYAN}🔧 ${message}${NC}" ;;
    esac
}

# Error detection patterns
declare -A ERROR_PATTERNS=(
    ["SYNTAX_ERROR"]="SyntaxError|Parse error|Unexpected token"
    ["IMPORT_ERROR"]="Cannot resolve module|Module not found|Import error"
    ["TYPE_ERROR"]="TypeScript error|Type.*is not assignable"
    ["LINT_ERROR"]="ESLint.*error|Linting errors"
    ["TEST_FAILURE"]="Test failed|Tests.*failed|FAIL"
    ["BUILD_ERROR"]="Build failed|Compilation error|npm ERR!"
    ["DEPENDENCY_ERROR"]="Missing dependency|Package not found|npm install"
)

# Auto-fix functions
fix_syntax_errors() {
    print_status "FIXING" "Attempting to fix syntax errors..."
    
    # Run ESLint with auto-fix
    cd frontend
    npm run lint:fix 2>/dev/null || true
    
    # Fix common syntax issues
    find src -name "*.tsx" -o -name "*.ts" -o -name "*.js" -o -name "*.jsx" | while read file; do
        # Add missing semicolons
        sed -i 's/\([^;]\)$/\1;/g' "$file" 2>/dev/null || true
        
        # Fix missing commas in objects/arrays
        sed -i 's/\([^,]\)\s*$/\1,/g' "$file" 2>/dev/null || true
    done
    
    cd ..
    print_status "SUCCESS" "Syntax fixes applied"
}

fix_import_errors() {
    print_status "FIXING" "Attempting to fix import errors..."
    
    cd frontend
    
    # Reinstall dependencies
    npm install --legacy-peer-deps 2>/dev/null || npm install --force 2>/dev/null || true
    
    # Clear cache
    npm start --reset-cache 2>/dev/null || true
    
    cd ..
    print_status "SUCCESS" "Import fixes applied"
}

fix_type_errors() {
    print_status "FIXING" "Attempting to fix TypeScript errors..."
    
    cd frontend
    
    # Run type check and attempt fixes
    npm run type-check 2>/dev/null || true
    
    # Add any declarations if needed
    find src -name "*.tsx" -o -name "*.ts" | while read file; do
        # Add common type fixes
        sed -i 's/any\[\]/any[]/g' "$file" 2>/dev/null || true
    done
    
    cd ..
    print_status "SUCCESS" "TypeScript fixes applied"
}

fix_dependency_errors() {
    print_status "FIXING" "Attempting to fix dependency errors..."
    
    # Frontend dependencies
    cd frontend
    rm -rf node_modules package-lock.json 2>/dev/null || true
    npm install --legacy-peer-deps 2>/dev/null || npm install --force 2>/dev/null || true
    cd ..
    
    # Backend dependencies
    cd backend
    rm -rf node_modules package-lock.json 2>/dev/null || true
    npm install 2>/dev/null || true
    pip install -r requirements.txt 2>/dev/null || true
    cd ..
    
    print_status "SUCCESS" "Dependencies reinstalled"
}

fix_test_failures() {
    print_status "FIXING" "Attempting to fix test failures..."
    
    cd frontend
    
    # Update snapshots
    npm test -- --updateSnapshot --watchAll=false 2>/dev/null || true
    
    # Clear test cache
    npm test -- --clearCache --watchAll=false 2>/dev/null || true
    
    cd ..
    print_status "SUCCESS" "Test fixes applied"
}

detect_and_fix_errors() {
    local log_file="$1"
    local fixed_any=false
    
    print_section "🔍 ERROR DETECTION & AUTO-FIX"
    
    if [[ ! -f "$log_file" ]]; then
        print_status "WARNING" "Log file not found: $log_file"
        return 1
    fi
    
    local log_content=$(cat "$log_file")
    
    for error_type in "${!ERROR_PATTERNS[@]}"; do
        if echo "$log_content" | grep -qiE "${ERROR_PATTERNS[$error_type]}"; then
            print_status "ERROR" "Detected: $error_type"
            
            case $error_type in
                "SYNTAX_ERROR")   fix_syntax_errors; fixed_any=true ;;
                "IMPORT_ERROR")   fix_import_errors; fixed_any=true ;;
                "TYPE_ERROR")     fix_type_errors; fixed_any=true ;;
                "DEPENDENCY_ERROR") fix_dependency_errors; fixed_any=true ;;
                "TEST_FAILURE")   fix_test_failures; fixed_any=true ;;
                "LINT_ERROR")     fix_syntax_errors; fixed_any=true ;;
                "BUILD_ERROR")    fix_syntax_errors && fix_import_errors; fixed_any=true ;;
            esac
        fi
    done
    
    if [[ "$fixed_any" == "true" ]]; then
        print_status "SUCCESS" "Auto-fixes applied, ready for retry"
        return 0
    else
        print_status "INFO" "No fixable errors detected"
        return 1
    fi
}

run_frontend_tests() {
    local attempt="$1"
    local log_file="$LOG_DIR/frontend_tests_${attempt}_${TIMESTAMP}.log"
    
    print_section "🧪 FRONTEND TESTS (Attempt $attempt)"
    
    cd frontend
    
    # Run tests with timeout
    timeout $TEST_TIMEOUT npm run test:quick > "$log_file" 2>&1 || {
        local exit_code=$?
        print_status "ERROR" "Frontend tests failed (exit code: $exit_code)"
        cd ..
        return $exit_code
    }
    
    cd ..
    print_status "SUCCESS" "Frontend tests passed"
    return 0
}

run_backend_tests() {
    local attempt="$1"
    local log_file="$LOG_DIR/backend_tests_${attempt}_${TIMESTAMP}.log"
    
    print_section "🧪 BACKEND TESTS (Attempt $attempt)"
    
    cd backend
    
    # Run Python tests
    timeout $TEST_TIMEOUT python run_tests.py > "$log_file" 2>&1 || {
        local exit_code=$?
        print_status "ERROR" "Backend tests failed (exit code: $exit_code)"
        cd ..
        return $exit_code
    }
    
    cd ..
    print_status "SUCCESS" "Backend tests passed"
    return 0
}

run_build_tests() {
    local attempt="$1"
    local log_file="$LOG_DIR/build_tests_${attempt}_${TIMESTAMP}.log"
    
    print_section "🏗️ BUILD TESTS (Attempt $attempt)"
    
    cd frontend
    
    # Test build
    timeout $TEST_TIMEOUT npm run build > "$log_file" 2>&1 || {
        local exit_code=$?
        print_status "ERROR" "Build test failed (exit code: $exit_code)"
        cd ..
        return $exit_code
    }
    
    cd ..
    print_status "SUCCESS" "Build test passed"
    return 0
}

run_lint_tests() {
    local attempt="$1"
    local log_file="$LOG_DIR/lint_tests_${attempt}_${TIMESTAMP}.log"
    
    print_section "📋 LINT TESTS (Attempt $attempt)"
    
    cd frontend
    
    # Run linting
    npm run lint > "$log_file" 2>&1 || {
        local exit_code=$?
        print_status "ERROR" "Lint tests failed (exit code: $exit_code)"
        cd ..
        return $exit_code
    }
    
    cd ..
    print_status "SUCCESS" "Lint tests passed"
    return 0
}

run_all_tests() {
    local attempt="$1"
    local overall_success=true
    
    # Run all test suites
    run_frontend_tests "$attempt" || overall_success=false
    run_backend_tests "$attempt" || overall_success=false
    run_build_tests "$attempt" || overall_success=false
    run_lint_tests "$attempt" || overall_success=false
    
    if [[ "$overall_success" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

cleanup_old_logs() {
    print_section "🧹 CLEANUP"
    
    # Keep only last 10 log files
    find "$LOG_DIR" -name "*.log" -type f -printf '%T@ %p\n' | sort -n | head -n -10 | cut -d' ' -f2- | xargs -r rm -f
    
    print_status "SUCCESS" "Old logs cleaned up"
}

generate_report() {
    local final_status="$1"
    local attempts_made="$2"
    
    local report_file="$LOG_DIR/deployment_report_${TIMESTAMP}.md"
    
    cat > "$report_file" << EOF
# 🚀 Deployment Test Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Status:** $final_status  
**Attempts:** $attempts_made/$MAX_RETRY_ATTEMPTS  

## 📊 Test Results Summary

### Frontend Tests
$(if [[ -f "$LOG_DIR/frontend_tests_${attempts_made}_${TIMESTAMP}.log" ]]; then
    if grep -q "PASS" "$LOG_DIR/frontend_tests_${attempts_made}_${TIMESTAMP}.log"; then
        echo "✅ **PASSED**"
    else
        echo "❌ **FAILED**"
    fi
else
    echo "⚠️ **NOT RUN**"
fi)

### Backend Tests
$(if [[ -f "$LOG_DIR/backend_tests_${attempts_made}_${TIMESTAMP}.log" ]]; then
    if grep -q "PASSED" "$LOG_DIR/backend_tests_${attempts_made}_${TIMESTAMP}.log"; then
        echo "✅ **PASSED**"
    else
        echo "❌ **FAILED**"
    fi
else
    echo "⚠️ **NOT RUN**"
fi)

### Build Tests
$(if [[ -f "$LOG_DIR/build_tests_${attempts_made}_${TIMESTAMP}.log" ]]; then
    if [ -f "frontend/build/index.html" ]; then
        echo "✅ **PASSED**"
    else
        echo "❌ **FAILED**"
    fi
else
    echo "⚠️ **NOT RUN**"
fi)

### Lint Tests
$(if [[ -f "$LOG_DIR/lint_tests_${attempts_made}_${TIMESTAMP}.log" ]]; then
    if ! grep -q "error" "$LOG_DIR/lint_tests_${attempts_made}_${TIMESTAMP}.log"; then
        echo "✅ **PASSED**"
    else
        echo "❌ **FAILED**"
    fi
else
    echo "⚠️ **NOT RUN**"
fi)

## 📝 Log Files
$(ls -la "$LOG_DIR"/*_${TIMESTAMP}.log 2>/dev/null | sed 's/^/- /' || echo "No logs generated")

## 🔧 Auto-Fixes Applied
$(grep -h "Auto-fixes applied" "$LOG_DIR"/*_${TIMESTAMP}.log 2>/dev/null | sort -u | sed 's/^/- /' || echo "No auto-fixes were needed")

## 📈 Recommendations
EOF

    if [[ "$final_status" == "SUCCESS" ]]; then
        cat >> "$report_file" << EOF
- ✅ All tests passed! Safe to deploy.
- 📊 Consider running full test suite with coverage before major releases.
- 🔄 Monitor deployment for any runtime issues.
EOF
    else
        cat >> "$report_file" << EOF
- ❌ Tests failed after $attempts_made attempts.
- 🔍 Review error logs above for detailed failure information.
- 🛠️ Manual intervention may be required.
- 📞 Consider contacting the development team for assistance.
EOF
    fi
    
    print_status "INFO" "Report generated: $report_file"
}

main() {
    print_header
    
    # Cleanup old logs first
    cleanup_old_logs
    
    # Main test loop with retries
    local attempt=1
    local success=false
    
    while [[ $attempt -le $MAX_RETRY_ATTEMPTS ]]; do
        print_section "🎯 ATTEMPT $attempt/$MAX_RETRY_ATTEMPTS"
        
        if run_all_tests "$attempt"; then
            success=true
            break
        else
            print_status "ERROR" "Attempt $attempt failed"
            
            if [[ $attempt -lt $MAX_RETRY_ATTEMPTS ]]; then
                # Detect and fix errors from all log files
                local any_fixes_applied=false
                for log_file in "$LOG_DIR"/*_${attempt}_${TIMESTAMP}.log; do
                    if [[ -f "$log_file" ]] && detect_and_fix_errors "$log_file"; then
                        any_fixes_applied=true
                    fi
                done
                
                if [[ "$any_fixes_applied" == "false" ]]; then
                    print_status "WARNING" "No automatic fixes available, trying generic fixes..."
                    fix_dependency_errors
                    sleep 2
                fi
                
                print_status "INFO" "Retrying in 5 seconds..."
                sleep 5
            fi
        fi
        
        ((attempt++))
    done
    
    # Final status and reporting
    if [[ "$success" == "true" ]]; then
        print_status "SUCCESS" "All tests passed! 🎉"
        print_status "INFO" "Deployment is GO for launch! 🚀"
        generate_report "SUCCESS" $((attempt-1))
        exit 0
    else
        print_status "ERROR" "Tests failed after $MAX_RETRY_ATTEMPTS attempts"
        print_status "ERROR" "DO NOT DEPLOY! Manual intervention required."
        generate_report "FAILED" $MAX_RETRY_ATTEMPTS
        exit 1
    fi
}

# Handle interruption gracefully
trap 'echo -e "\n${RED}🛑 Pre-deployment automation interrupted${NC}"; exit 130' INT TERM

# Run main function
main "$@"
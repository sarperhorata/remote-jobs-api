#!/usr/bin/env python3
"""
Pre-commit test runner for Buzz2Remote backend.
Runs essential tests and blocks deployment if they fail.
Priority: Syntax → Unit → API → Integration
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Main test runner."""
    print(f"""
🧪 Pre-Commit Test Suite
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Priority: Syntax → Unit → API → Integration
""")
    
    # Tests to run in priority order (most critical first)
    tests = [
        ("🔍 Syntax & Import Tests", "pytest tests/syntax/ -q"),
        ("🔧 Unit Tests", "pytest tests/unit/ -q"),
        ("🌐 Basic API Tests", "pytest tests/api/test_health.py -q"),
        ("🔗 Database Tests", "pytest tests/unit/test_database.py -q"),
    ]
    
    all_passed = True
    
    for test_name, cmd in tests:
        print(f"Running {test_name}...")
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
            print(f"Error: {stderr}")
            all_passed = False
            # Stop at first failure for faster feedback
            break
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Safe to deploy.")
        print("💡 Run 'pytest --cov=.' for full test suite with coverage")
        return 0
    else:
        print("💥 TESTS FAILED! DO NOT DEPLOY!")
        print("🔧 Fix the failing tests before committing.")
        print("📝 Most likely issues:")
        print("   - Syntax errors (indentation, missing colons)")
        print("   - Import errors (missing dependencies)")
        print("   - Basic logic errors")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
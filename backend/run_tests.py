#!/usr/bin/env python3
"""
Test runner script for Buzz2Remote backend.
Runs all tests with proper error handling and reporting.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print("-" * 60)
    
    try:
        # Split command into list to avoid shell=True
        if isinstance(cmd, str):
            cmd_list = cmd.split()
        else:
            cmd_list = cmd
            
        result = subprocess.run(
            cmd_list, 
            shell=False, 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Print output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"\nExit code: {result.returncode}")
        
        if result.returncode != 0:
            print(f"❌ {description} FAILED")
            return False
        else:
            print(f"✅ {description} PASSED")
            return True
            
    except Exception as e:
        print(f"❌ Error running {description}: {str(e)}")
        return False

def main():
    """Main test runner function."""
    print(f"""
🚀 Buzz2Remote Backend Test Suite
Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python: {sys.version}
Working Directory: {os.getcwd()}
""")
    
    # List of test commands to run
    test_commands = [
        # Basic test discovery
        ("pytest --version", "Check pytest installation"),
        
        # Run all tests with verbose output
        ("pytest -v", "Run all tests (verbose)"),
        
        # Run tests by category
        ("pytest -v -m unit", "Run unit tests only"),
        ("pytest -v -m api", "Run API tests only"), 
        ("pytest -v -m integration", "Run integration tests only"),
        
        # Run with coverage
        ("pytest --cov=. --cov-report=term-missing", "Run with coverage report"),
        
        # Generate HTML coverage report
        ("pytest --cov=. --cov-report=html:htmlcov", "Generate HTML coverage report"),
        
        # Run performance tests (if any)
        ("pytest -v -m slow", "Run slow/performance tests"),
    ]
    
    results = []
    
    for cmd, description in test_commands:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<10} {description}")
    
    print(f"\nResults: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📈 Coverage report available at: htmlcov/index.html")
        return 0
    else:
        print(f"\n💥 {total - passed} TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
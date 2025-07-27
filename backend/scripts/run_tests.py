#!/usr/bin/env python3
"""
Test Runner Script for Backend
Optimized for CI/CD and local development
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, timeout=300):
    """Run a command with timeout"""
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=Path(__file__).parent.parent
        )
        duration = time.time() - start_time
        print(f"✅ Command completed in {duration:.2f}s: {cmd}")
        return result
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after {timeout}s: {cmd}")
        return None
    except Exception as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e}")
        return None

def main():
    """Main test runner"""
    print("🚀 Starting Backend Test Suite...")
    
    # Set environment variables
    os.environ["TESTING"] = "true"
    os.environ["ENVIRONMENT"] = "test"
    os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
    os.environ.setdefault("DATABASE_NAME", "test_buzz2remote")
    
    # Test phases
    phases = [
        {
            "name": "Sanity Tests",
            "cmd": "python -m pytest tests/test_sanity.py -v --timeout=10",
            "timeout": 60
        },
        {
            "name": "Unit Tests",
            "cmd": "python -m pytest tests/unit/ -v --timeout=15 -m 'not slow'",
            "timeout": 120
        },
        {
            "name": "API Tests",
            "cmd": "python -m pytest tests/api/ -v --timeout=20 -m 'not slow'",
            "timeout": 180
        },
        {
            "name": "Integration Tests",
            "cmd": "python -m pytest tests/integration/ -v --timeout=30 -m 'not slow'",
            "timeout": 300
        }
    ]
    
    results = []
    
    for phase in phases:
        print(f"\n📋 Running {phase['name']}...")
        result = run_command(phase['cmd'], phase['timeout'])
        results.append((phase['name'], result))
        
        if result and result.returncode != 0:
            print(f"❌ {phase['name']} failed!")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return 1
    
    # Generate coverage report
    print("\n📊 Generating Coverage Report...")
    coverage_cmd = "python -m pytest tests/ --cov=backend --cov-report=term-missing --cov-report=html --cov-fail-under=70"
    coverage_result = run_command(coverage_cmd, 300)
    
    if coverage_result and coverage_result.returncode != 0:
        print("❌ Coverage requirements not met!")
        return 1
    
    # Performance summary
    print("\n⚡ Performance Summary...")
    perf_cmd = "python -m pytest tests/ --durations=5 --tb=short"
    perf_result = run_command(perf_cmd, 120)
    
    print("\n🎉 All tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Enhanced Test Runner for Buzz2Remote Backend
Provides comprehensive testing with different test suites and detailed reporting.
"""

import subprocess
import sys
import os
import argparse
import time
import json
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Enhanced test runner with multiple test suites and reporting."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.start_time = None
        
    def run_command(self, cmd, description="", capture_output=True):
        """Run a command and handle errors."""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
        print(f"Command: {cmd}")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=capture_output, 
                text=True,
                cwd=self.project_root
            )
            
            if capture_output:
                if result.stdout:
                    print("STDOUT:")
                    print(result.stdout)
                
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)
            
            print(f"\nExit code: {result.returncode}")
            
            if result.returncode != 0:
                print(f"❌ {description} FAILED")
                return False, result
            else:
                print(f"✅ {description} PASSED")
                return True, result
                
        except Exception as e:
            print(f"❌ Error running {description}: {str(e)}")
            return False, None

    def run_unit_tests(self, verbose=False):
        """Run unit tests."""
        cmd = "python -m pytest tests/unit/ -m unit"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "Unit Tests")
        self.test_results['unit'] = {
            'success': success,
            'result': result
        }
        return success

    def run_api_tests(self, verbose=False):
        """Run API tests."""
        cmd = "python -m pytest tests/api/ -m api"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "API Tests")
        self.test_results['api'] = {
            'success': success,
            'result': result
        }
        return success

    def run_integration_tests(self, verbose=False):
        """Run integration tests."""
        cmd = "python -m pytest tests/integration/ -m integration"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "Integration Tests")
        self.test_results['integration'] = {
            'success': success,
            'result': result
        }
        return success

    def run_security_tests(self, verbose=False):
        """Run security tests."""
        cmd = "python -m pytest -m security"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "Security Tests")
        self.test_results['security'] = {
            'success': success,
            'result': result
        }
        return success

    def run_performance_tests(self, verbose=False):
        """Run performance tests."""
        cmd = "python -m pytest -m performance"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "Performance Tests")
        self.test_results['performance'] = {
            'success': success,
            'result': result
        }
        return success

    def run_coverage_tests(self, verbose=False):
        """Run tests with coverage reporting."""
        cmd = "python -m pytest --cov=. --cov-report=term-missing --cov-report=html:htmlcov"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "Coverage Tests")
        self.test_results['coverage'] = {
            'success': success,
            'result': result
        }
        return success

    def run_smoke_tests(self, verbose=False):
        """Run smoke tests for basic functionality."""
        cmd = "python -m pytest -m smoke"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "Smoke Tests")
        self.test_results['smoke'] = {
            'success': success,
            'result': result
        }
        return success

    def run_regression_tests(self, verbose=False):
        """Run regression tests."""
        cmd = "python -m pytest -m regression"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, "Regression Tests")
        self.test_results['regression'] = {
            'success': success,
            'result': result
        }
        return success

    def run_all_tests(self, verbose=False):
        """Run all test suites."""
        print(f"""
🚀 Buzz2Remote Enhanced Test Suite
Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python: {sys.version}
Working Directory: {self.project_root}
""")
        
        self.start_time = time.time()
        
        # Run all test suites
        test_suites = [
            ("Smoke Tests", self.run_smoke_tests),
            ("Unit Tests", self.run_unit_tests),
            ("API Tests", self.run_api_tests),
            ("Integration Tests", self.run_integration_tests),
            ("Security Tests", self.run_security_tests),
            ("Performance Tests", self.run_performance_tests),
            ("Coverage Tests", self.run_coverage_tests),
            ("Regression Tests", self.run_regression_tests),
        ]
        
        results = []
        
        for suite_name, suite_func in test_suites:
            try:
                success = suite_func(verbose)
                results.append((suite_name, success))
            except Exception as e:
                print(f"❌ Error in {suite_name}: {str(e)}")
                results.append((suite_name, False))
        
        return results

    def generate_report(self, results):
        """Generate comprehensive test report."""
        end_time = time.time()
        total_time = end_time - self.start_time if self.start_time else 0
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n{'='*60}")
        print("📊 COMPREHENSIVE TEST REPORT")
        print(f"{'='*60}")
        print(f"Test Execution Time: {total_time:.2f} seconds")
        print(f"Total Test Suites: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print(f"\n{'='*60}")
        print("📋 DETAILED RESULTS")
        print(f"{'='*60}")
        
        for suite_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status:<10} {suite_name}")
        
        # Quality assessment
        print(f"\n{'='*60}")
        print("🎯 QUALITY ASSESSMENT")
        print(f"{'='*60}")
        
        if passed == total:
            print("🏆 EXCELLENT: All test suites passed!")
            print("✅ Code quality is high")
            print("✅ System is ready for deployment")
        elif passed >= total * 0.8:
            print("🟡 GOOD: Most test suites passed")
            print("⚠️  Some issues need attention")
            print("🔧 Review failed tests before deployment")
        else:
            print("🔴 POOR: Multiple test suites failed")
            print("❌ Code quality needs improvement")
            print("🚫 Do not deploy until issues are resolved")
        
        # Recommendations
        print(f"\n{'='*60}")
        print("💡 RECOMMENDATIONS")
        print(f"{'='*60}")
        
        if passed < total:
            failed_suites = [name for name, success in results if not success]
            print(f"🔧 Fix issues in: {', '.join(failed_suites)}")
            print("📝 Review test logs for detailed error information")
            print("🔄 Re-run tests after fixes")
        
        if total_time > 300:  # 5 minutes
            print("⚡ Consider optimizing slow test suites")
        
        if passed == total:
            print("🚀 Ready for production deployment")
            print("📈 Consider adding more edge case tests")
        
        return passed == total

    def run_specific_tests(self, test_pattern, verbose=False):
        """Run specific tests by pattern."""
        cmd = f"python -m pytest {test_pattern}"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, f"Specific Tests: {test_pattern}")
        return success

    def run_tests_with_marker(self, marker, verbose=False):
        """Run tests with specific marker."""
        cmd = f"python -m pytest -m {marker}"
        if verbose:
            cmd += " -v"
        
        success, result = self.run_command(cmd, f"Tests with marker: {marker}")
        return success

    def check_test_environment(self):
        """Check if test environment is properly set up."""
        print("🔍 Checking test environment...")
        
        checks = [
            ("Python version", "python --version"),
            ("Pytest installation", "python -m pytest --version"),
            ("Test directory exists", f"test -d {self.project_root}/tests"),
            ("Requirements installed", "python -c 'import pytest, fastapi, motor'"),
        ]
        
        all_good = True
        for check_name, check_cmd in checks:
            try:
                if check_cmd.startswith("test -d"):
                    # Directory check
                    path = check_cmd.split()[-1]
                    exists = os.path.exists(path)
                    status = "✅" if exists else "❌"
                    print(f"{status} {check_name}: {'OK' if exists else 'MISSING'}")
                    if not exists:
                        all_good = False
                else:
                    # Command check
                    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                    status = "✅" if result.returncode == 0 else "❌"
                    print(f"{status} {check_name}: {'OK' if result.returncode == 0 else 'FAILED'}")
                    if result.returncode != 0:
                        all_good = False
            except Exception as e:
                print(f"❌ {check_name}: ERROR - {str(e)}")
                all_good = False
        
        return all_good

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Enhanced Test Runner for Buzz2Remote Backend")
    parser.add_argument("--suite", choices=["all", "unit", "api", "integration", "security", "performance", "coverage", "smoke", "regression"], 
                       default="all", help="Test suite to run")
    parser.add_argument("--pattern", help="Run specific tests matching pattern")
    parser.add_argument("--marker", help="Run tests with specific marker")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-env", action="store_true", help="Check test environment")
    parser.add_argument("--report-only", action="store_true", help="Generate report only")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Check environment if requested
    if args.check_env:
        if not runner.check_test_environment():
            print("❌ Test environment check failed. Please fix issues before running tests.")
            sys.exit(1)
        print("✅ Test environment is ready!")
        return
    
    # Run specific test pattern
    if args.pattern:
        success = runner.run_specific_tests(args.pattern, args.verbose)
        sys.exit(0 if success else 1)
    
    # Run tests with specific marker
    if args.marker:
        success = runner.run_tests_with_marker(args.marker, args.verbose)
        sys.exit(0 if success else 1)
    
    # Run specific test suite
    if args.suite != "all":
        suite_methods = {
            "unit": runner.run_unit_tests,
            "api": runner.run_api_tests,
            "integration": runner.run_integration_tests,
            "security": runner.run_security_tests,
            "performance": runner.run_performance_tests,
            "coverage": runner.run_coverage_tests,
            "smoke": runner.run_smoke_tests,
            "regression": runner.run_regression_tests,
        }
        
        if args.suite in suite_methods:
            success = suite_methods[args.suite](args.verbose)
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Unknown test suite: {args.suite}")
            sys.exit(1)
    
    # Run all tests
    results = runner.run_all_tests(args.verbose)
    overall_success = runner.generate_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()